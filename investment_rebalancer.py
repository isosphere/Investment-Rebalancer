#!/usr/bin/env python
# Investment Rebalancer
# Written by Matthew Scheffel <mscheffel@gmail.com>

# Assumes you have three "buckets" of investment - local market shares, local bonds, and global market shares
# Offers a suggestion for reinvestment without selling any existing shares/bonds such that you will bring your 
# portfolio as close to your target distribution as possible

from __future__ import division

from math import sqrt
from time import time

def total_investment_value(portfolio):
    value = 0
    for investment_bucket in portfolio:
        value += portfolio[investment_bucket]
    return value

def investment_balance(portfolio):
    total_value = total_investment_value(portfolio)
    portfolio_balance = {}
    
    for investment_bucket in portfolio:
        portfolio_balance[investment_bucket] = portfolio[investment_bucket]/total_value

    return portfolio_balance

def investment_error_percent(portfolio, target):
    portfolio_balance = investment_balance(portfolio)

    investment_error = {}

    for investment_bucket in portfolio:
        investment_error[investment_bucket] = target[investment_bucket] - portfolio_balance[investment_bucket]

    return investment_error


def investment_error_metric(portfolio, target):
    portfolio_balance = investment_balance(portfolio)

    error_sum = 0
    bucket_count = 0

    for investment_bucket in portfolio:
        # squaring the error to take into account negative error which is undesirable
        error_sum += (target[investment_bucket] - portfolio_balance[investment_bucket])**2
        bucket_count += 1

    return 100*error_sum/bucket_count

def pretty_print(portfolio, target):
    total_value = total_investment_value(portfolio)
    investment_distribution = investment_balance(portfolio)
    investment_error = investment_error_percent(portfolio, target)
    string = ""

    string += "Bucket\t\tValue\t\tShare\tTarget\tError\n"
    for bucket in portfolio:
        string += "%s\t$%.2f \t%.1f%%\t%.1f%%\t%.1f%%\n" % (bucket, portfolio[bucket], 100*investment_distribution[bucket], 100*target[bucket], 100*investment_error[bucket])

    string += "\nTotal value: $%.2f\nError Metric: %.2f\n" % (total_value, investment_error_metric(portfolio, target))
    
    return string

def brute_force_seek_optimium_balance(max_capital, portfolio, target, margin):
    best_error = investment_error_metric(portfolio, target)
    new_portfolio = {}
    reinvestment_for_best = 0

    for reinvestment_budget in range(0, max_capital+1, 200):
        for local_market_reinvestment_share in range (0, 100):
            for local_bond_reinvestment_share in range (0, 100 - local_market_reinvestment_share):
                for global_market_reinvestment_share in range (0, 100 - (local_market_reinvestment_share + local_bond_reinvestment_share)):
                    new_portfolio = {
                        'local_market'  : portfolio['local_market']  + local_market_reinvestment_share/100*reinvestment_budget,
                        'local_bonds'   : portfolio['local_bonds']   + local_bond_reinvestment_share/100*reinvestment_budget,
                        'global_market' : portfolio['global_market'] + global_market_reinvestment_share/100*reinvestment_budget,
                    }
                    new_error = investment_error_metric(new_portfolio, target)

                    if new_error < best_error:
                        best_error = new_error
                        best_result = new_portfolio
                        reinvestment_for_best = reinvestment_budget

                    if sqrt(new_error/100) <= margin:
                        return (best_result, reinvestment_for_best)

    return (best_result, reinvestment_for_best)

# Moderately close to the brute force result, but the brute force result is better
def quick_balance(max_capital, portfolio, target, margin):
    errors = investment_error_percent(portfolio, target)

    to_delete = []
    for bucket in errors:
        if errors[bucket] < 0:
            to_delete.append(bucket)

    for bucket in to_delete:
        del errors[bucket]

    total_error = 0
    for bucket in errors:
        total_error += errors[bucket]

    total_invested_already = 0
    for bucket in errors:
        total_invested_already += portfolio[bucket]

    for bucket in errors:
        portfolio[bucket] = portfolio[bucket] + max_capital *  portfolio[bucket]/ total_invested_already

    return (portfolio, max_capital)

local_market_value = 10000
local_bond_value = 15000
global_market_value = 11000

local_market_target = 0.20
local_bond_target = 0.40
global_market_target = 0.40

investment_budget = 10000 

investment_portfolio = {
    'local_market' : local_market_value,
    'global_market': global_market_value,
    'local_bonds'  : local_bond_value
}

investment_target = {
    'local_market'  : local_market_target,
    'local_bonds'   : local_bond_target,
    'global_market' : global_market_target
}

print "Initial Investment Portfolio:\n"
print pretty_print(investment_portfolio, investment_target)

# Brute force optimum solution finding

portfolio_error_margin = 2 / 100 # acceptable target error in percent. not very precise.

print "\nFinding optimum rebalance with a budget of $%.2f, allowing for about %.2f%% error (very roughly)" % (investment_budget, 100*portfolio_error_margin)
start_time = time()
(new_portfolio, investment_budget) = brute_force_seek_optimium_balance(investment_budget, investment_portfolio, investment_target, portfolio_error_margin)
#(new_portfolio, investment_budget) = quick_balance(investment_budget, investment_portfolio, investment_target, portfolio_error_margin)

print "\nDone. Best result occured for budget of $%.2f\nTook %.3f seconds.\n\n" % (investment_budget, time() - start_time)

print "\nReinvestment amounts for rebalance:\n"
for bucket in new_portfolio:
    print "%s \t+= $%.2f\n" % (bucket, new_portfolio[bucket] - investment_portfolio[bucket])

print "\n"

print pretty_print(new_portfolio, investment_target)

print "\n\nNote: error metric is 100*[(local_market_target % - local_market_actual %)**2 + (local_bonds_target % - local_bonds_actual %)**2 + (global_market_target % - global_market_actual %)**2)]/3\n"
print "Note: program uses dollars and investment types like 'local market' and 'local bonds' but it doesn't actually matter what you are using it for\n"
