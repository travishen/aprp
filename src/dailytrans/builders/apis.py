from django.db.models import Q
import datetime
import json
from .utils import date_transfer
from .abstract import AbstractApi
from dailytrans.models import DailyTran


class Api(AbstractApi):

    # Settings
    API_NAME = 'apis'
    ZFILL = False
    ROC_FORMAT = True
    SEP = '/'

    # Filters
    START_YEAR_FILTER = 'startYear=%s'
    END_YEAR_FILTER = 'endYear=%s'
    START_MONTH_FILTER = 'startMonth=%s'
    END_MONTH_FILTER = 'endMonth=%s'
    START_DATE_FILTER = 'startDay=%s'
    END_DATE_FILTER = 'endDay=%s'
    NAME_FILTER = 'productName=%s'

    def __init__(self, model, config_code, type_id, logger_type_code=None):
        super(Api, self).__init__(model=model, config_code=config_code, type_id=type_id,
                                  logger='aprp', logger_type_code=logger_type_code)

    def hook(self, dic):
        for key, value in dic.items():
            if isinstance(value, str):
                dic[key] = value.strip()

        product_name = dic.get('PRODUCTNAME')
        source_name = dic.get('ORGNAME')
        product = self.PRODUCT_QS.filter(code=product_name).first()
        source = self.SOURCE_QS.filter(name=source_name).first()
        if product and source:
            tran = DailyTran(
                product=product,
                source=source,
                avg_price=float(dic.get('AVGPRICE')),
                date=date_transfer(sep=self.SEP, string=dic.get('PERIOD'), roc_format=self.ROC_FORMAT)
            )
            return tran
        else:
            if product_name and not product:
                self.LOGGER.warning('Cannot Match Product: %s' % (product_name),
                                    extra=self.LOGGER_EXTRA)
            if source_name and source_name != '當日平均價' and not source:
                self.LOGGER.warning('Cannot Match Source: %s' % (source_name),
                                    extra=self.LOGGER_EXTRA)
            return dic

    def request(self, start_date=None, end_date=None, source=None, code=None, name=None):
        url = self.API_URL
        if start_date:
            if not isinstance(start_date, datetime.date):
                raise NotImplementedError

            url = '&'.join((url, self.START_DATE_FILTER % start_date.day))
            url = '&'.join((url, self.START_MONTH_FILTER % start_date.month))
            url = '&'.join((url, self.START_YEAR_FILTER % start_date.year))

        if end_date:
            if not isinstance(end_date, datetime.date):
                raise NotImplementedError

            url = '&'.join((url, self.END_DATE_FILTER % end_date.day))
            url = '&'.join((url, self.END_MONTH_FILTER % end_date.month))
            url = '&'.join((url, self.END_YEAR_FILTER % end_date.year))

        if start_date and end_date:
            if start_date > end_date:
                raise AttributeError

        if name:
            url = '&'.join((url, self.NAME_FILTER % name))

        return self.get(url, verify=False)

    def load(self, response):
        data = []
        if response.text:
            try:
                data_set = json.loads(response.text, object_hook=self.hook)
                data = data_set['DATASET']
            except Exception as e:
                self.LOGGER.exception('%s \n%s' % (response.request.url, e), extra=self.LOGGER_EXTRA)

        # data should look like [D, B, {}, C, {}...] after loads
        for obj in data:
            if isinstance(obj, DailyTran):
                try:
                    # update if exists
                    daily_tran_qs = DailyTran.objects.filter(Q(date__exact=obj.date)
                                                             & Q(product=obj.product))
                    if obj.source:
                        daily_tran_qs = daily_tran_qs.filter(source=obj.source)

                    if daily_tran_qs.count() > 1:
                        # log as duplicate
                        items = str(daily_tran_qs.values_list('id', flat=True))
                        self.LOGGER.warning('Find duplicate DailyTran item: %s' % items, extra=self.LOGGER_EXTRA)

                    elif daily_tran_qs.count() == 1:
                        daily_tran_qs.update(avg_price=obj.avg_price)
                    else:
                        if obj.avg_price > 0:
                            obj.save()

                except Exception as e:
                    self.LOGGER.exception(e, extra=self.LOGGER_EXTRA)
