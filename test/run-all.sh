#!/bin/sh
# Use timestamp to make temporary directory name unique
NOW=$(date +%s)
TEMPORARY_DIR="temporary"$NOW

echo "Running all tests..."

echo "Running synthetic_hashpans"
mkdir -p "$TEMPORARY_DIR"/synthetic_hashpans
cst rtd transactionfilter --action synthetic_hashpans --pans-prefix "prefix_" --hashpans-qty 50 --salt "SALT876" > "$TEMPORARY_DIR"/synthetic_hashpans/hashpans.txt
if [ -z "$(cat "$TEMPORARY_DIR"/synthetic_hashpans/hashpans.txt)" ]
then
  echo "FAIL"
  exit 2
fi
echo "Done"

echo "Running synthetic_transactions"
cst rtd transactionfilter --action synthetic_transactions --pans-prefix "prefix_" --pans-qty 20000 --trx-qty 100 --ratio 5 --pos-number 10000 --salt "SALT987" -o "$TEMPORARY_DIR"/synthetic_transactions
if [ -n "$(find "$TEMPORARY_DIR"/synthetic_transactions -empty)" ]
then
  echo "FAIL"
  exit 2
fi

echo "Running synthetic_transactions pgp"
cst rtd transactionfilter --action synthetic_transactions --pans-prefix "prefix_" --pans-qty 20000 --trx-qty 100 --ratio 5 --pos-number 10000 --salt "SALT987" -o "$TEMPORARY_DIR"/synthetic_transactions_pgp --pgp --key ./public.key
if [ -n "$(find "$TEMPORARY_DIR"/synthetic_transactions_pgp -empty)" ]
then
  echo "FAIL"
  exit 2
fi

echo "Running synthetic_cards"
cst rtd transactionfilter --action synthetic_cards --pans-prefix "prefix_" --crd-qty 10 --par RANDOM --max-num-children 5  -o "$TEMPORARY_DIR"/synthetic_cards
if [ -n "$(find "$TEMPORARY_DIR"/synthetic_cards -empty)" ]
then
  echo "FAIL"
  exit 2
fi

echo "Running aggregate_transactions"
cst tae transactionaggregate --action aggregate_transactions --aggr-qty 9000 --reverse-ratio 100 --ratio-dirty-pos-type 30 --ratio-dirty-vat 20 --shuffle -o "$TEMPORARY_DIR"/aggregate_transactions
if [ -n "$(find "$TEMPORARY_DIR"/aggregate_transactions -empty)" ]
then
  echo "FAIL"
  exit 2
fi


echo "Running aggregate_transactions pgp"
cst tae transactionaggregate --action aggregate_transactions --aggr-qty 9000 --reverse-ratio 100 --ratio-dirty-pos-type 30 --ratio-dirty-vat 20 --shuffle -o "$TEMPORARY_DIR"/aggregate_transactions_pgp --pgp --key ./public.key
if [ -n "$(find "$TEMPORARY_DIR"/aggregate_transactions_pgp -empty)" ]
then
  echo "FAIL"
  exit 2
fi

echo "Running synthetic_results"
cst tae results --action synthetic_results --res-qty 10 -o "$TEMPORARY_DIR"/synthetic_results
if [ -n "$(find "$TEMPORARY_DIR"/synthetic_results -empty)" ]
then
  echo "FAIL"
  exit 2
fi

echo "Running synthetic_results zip"
cst tae results --action synthetic_results --res-qty 10 --gzip -o "$TEMPORARY_DIR"/synthetic_results_zip
if [ -n "$(find "$TEMPORARY_DIR"/synthetic_results_zip -empty)" ]
then
  echo "FAIL"
  exit 2
fi

echo "Running synthetic_reports"
cst tae registryreports --action synthetic_reports --rep-qty 10 -o "$TEMPORARY_DIR"/synthetic_reports
if [ -n "$(find "$TEMPORARY_DIR"/synthetic_reports -empty)" ]
then
  echo "FAIL"
  exit 2
fi

echo "Running trx_and_aggr"
cst sender aggregates --sender 99999 --action trx_and_aggr --aggr-qty 10 -o "$TEMPORARY_DIR"/trx_and_aggr
if [ -n "$(find "$TEMPORARY_DIR"/trx_and_aggr -empty)" ]
then
  echo "FAIL"
fi

echo "Running trx_and_aggr schema"
cst sender aggregates --sender COBAN --action trx_and_aggr --aggr-qty 10 -o "$TEMPORARY_DIR"/trx_and_aggr_schema
if [ -n "$(find "$TEMPORARY_DIR"/trx_and_aggr_schema -empty)" ]
then
  echo "FAIL"
fi

echo "Running contracts"
mkdir -p "$TEMPORARY_DIR"/contracts
cst wallet contracts --action fake_wallet_migration --contracts-qty 100 --ratio-delete-contract 5 --ratio-ko-delete-contract 2 --out "$TEMPORARY_DIR"/contracts
if [ -n "$(find "$TEMPORARY_DIR"/contracts -empty)" ]
then
  echo "FAIL"
fi

rm -rf "$TEMPORARY_DIR"
