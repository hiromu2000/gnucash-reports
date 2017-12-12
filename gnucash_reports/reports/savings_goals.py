import time
from datetime import datetime
from decimal import Decimal

from dateutil.relativedelta import relativedelta
from dateutil.rrule import rrule, MONTHLY

from gnucash_reports.configuration.currency import get_currency
from gnucash_reports.periods import PeriodStart
from gnucash_reports.wrapper import get_account, get_balance_on_date, account_walker


def savings_goal(definition):
    accounts = definition['account']
    if isinstance(accounts, basestring):
        accounts = [accounts]

    goal_amount = Decimal(definition.get('goal', Decimal(0.0)))

    as_of = PeriodStart(definition.get('as_of', PeriodStart.today))
    contributions = definition.get('contributions', [])

    if not hasattr(contributions, 'sort'):
        contributions = [contributions]

    total_balance = Decimal('0.0')
    currency = get_currency()

    for account_description in accounts:
        multiplier = Decimal('1.0')
        if isinstance(account_description, basestring):
            account = account_description
        else:
            account = account_description[0]
            multiplier = Decimal(account_description[1])

        for account_name in account_walker([account]):
            balance = get_balance_on_date(account_name, as_of.date, currency)
            total_balance += (balance * multiplier)

    for contribution in contributions:
        total_balance += Decimal(contribution)

    return dict(balance=total_balance, goal=goal_amount)


def savings_goal_trend(definition):
    account_name = definition.get('account_name')
    past_trend = definition.get('past_trend', 12)
    future_trend = definition.get('future_trend', 6)

    account = get_account(account_name)

    todays_date = datetime.today()
    beginning_of_month = datetime(todays_date.year, todays_date.month, 1)

    start_of_trend = beginning_of_month - relativedelta(months=past_trend)
    end_of_trend = start_of_trend + relativedelta(months=past_trend + future_trend)

    trend = []
    for dt in rrule(MONTHLY, dtstart=start_of_trend, until=end_of_trend):
        time_value = time.mktime(dt.timetuple())

        balance = get_balance_on_date(account, time_value)
        trend.append(dict(date=dt.strftime('%Y-%m-%d'), balance=balance))

    return dict(trend=trend)