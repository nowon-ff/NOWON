from pyspark.sql import SparkSession
import pandas as pd

from typing import Dict, Iterable

from google.analytics.data_v1beta import BetaAnalyticsDataClient
from google.analytics.data_v1beta.types import RunReportRequest,\
  Dimension, Metric, DateRange, Row

class GA4:
  _client = None
  _spark = None

  def __init__(self, service_account_json: str, spark: SparkSession = None):
    self._client = BetaAnalyticsDataClient\
      .from_service_account_json(service_account_json)
    self._spark = spark

  def get_data(
    self,
    property_id: str,
    dimensions: Iterable['str'],
    metrics: Iterable['str'],
    start_date: 'str',
    end_date: 'str',
    offset: int = 0,
    page_size: int = 100000,
    limit: int = -1,
  ):
    report = []
    print('Downloading first page...')
    first_page = self._run_report_request(
        property_id=property_id,
        dimensions=dimensions,
        metrics=metrics,
        start_date=start_date,
        end_date=end_date,
        offset=offset,
        page_size=limit if limit != -1 and limit <= page_size else page_size,
      )

    total_rows = limit if limit != -1 else int(first_page.row_count)
    report.extend(
        self._rows_to_dict(
          ga_rows=first_page.rows,
          dimension_headers=first_page.dimension_headers,
          metric_headers=first_page.metric_headers,
        )
      )

    print(f'Downloaded [{len(report)}] of total [{total_rows}] rows')

    if (limit != -1 and limit <= page_size):
      return self._create_dataframe(report)

    for off in range(offset + page_size, total_rows, page_size):
      page = self._run_report_request(
          property_id=property_id,
          dimensions=dimensions,
          metrics=metrics,
          start_date=start_date,
          end_date=end_date,
          offset=off,
          page_size=page_size,
        )
      report.extend(
          self._rows_to_dict(
              ga_rows=page.rows,
              dimension_headers=page.dimension_headers,
              metric_headers=page.metric_headers,
            )
        )
      print(f'Downloaded [{len(report)}] of total [{total_rows}] rows')

    print('Creating DataFrame with ' + 'Spark' if self._spark is not None else 'Pandas')

    return self._create_dataframe(report)

  def _run_report_request(
    self,
    property_id: str,
    dimensions: Iterable['str'],
    metrics: Iterable['str'],
    start_date: 'str',
    end_date: 'str',
    offset: int,
    page_size: int,
  ):
    dimensions_ga4 = []
    for dimension in dimensions:
      dimensions_ga4.append(Dimension(name=dimension))

    metrics_ga4 = []
    for metric in metrics:
      metrics_ga4.append(Metric(name=metric))

    request = RunReportRequest(
        property=f'properties/{property_id}',
        dimensions=dimensions_ga4,
        metrics=metrics_ga4,
        offset = offset,
        limit = page_size,
        date_ranges=[DateRange(start_date=start_date, end_date=end_date)]
      )

    return self._client.run_report(request)

  def _rows_to_dict(
    self,
    ga_rows: Iterable[Row],
    dimension_headers: Iterable[str],
    metric_headers: Iterable[str],
  ):
    rows = []

    dimension_len = len(dimension_headers)
    metric_len = len(metric_headers)

    for ga_row in ga_rows:
      row = {}
      for i in range(0, dimension_len):
        row.update({dimension_headers[i].name: ga_row.dimension_values[i].value})
      for i in range(0, metric_len):
        row.update({metric_headers[i].name: ga_row.metric_values[i].value})
      rows.append(row)

    return rows

  def _create_dataframe(self, report: Iterable[Dict]):
    if self._spark is not None:
      rdd = self._spark.sparkContext.parallelize(report)
      return self._spark.read.json(rdd)

    return pd.DataFrame(report)
