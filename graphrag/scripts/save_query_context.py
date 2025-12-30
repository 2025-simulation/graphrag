#!/usr/bin/env python3
"""
Utility script: run a basic query and save the returned context_data to the configured output storage.

Usage (example):
    python3 -m graphrag/scripts/save_query_context.py --root ./smallTest --query "生成一个普通的球形" --method local --output-key my_query_context.json

This script does NOT change the project source. It:
 - loads a GraphRagConfig using the same loader as the CLI
 - reads the necessary index table(s) (text_units for basic search)
 - calls the API `basic_search` to get (response, context_data)
 - formats context_data with `reformat_context_data` and saves as JSON to the configured output storage

Note: storage.set is asynchronous; we use asyncio.run(...) to call it.
"""

from __future__ import annotations

import argparse
import asyncio
import json
import logging
from pathlib import Path
from typing import Any

import graphrag.api as api
from graphrag.config.load_config import load_config
from graphrag.utils.api import create_storage_from_config, reformat_context_data
from graphrag.utils.storage import load_table_from_storage

logger = logging.getLogger(__name__)


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Run a basic query and save context_data to output storage.")
    p.add_argument("--root", type=Path, default=Path('.'), help="Project root directory (where settings.yaml lives)")
    p.add_argument("--config", type=Path, default=None, help="Optional config file path (settings.yaml) relative to root")
    p.add_argument("--query", type=str, required=True, help="Query string to run")
    p.add_argument(
        "--method",
        type=str,
        choices=("basic", "local"),
        default="basic",
        help="Which search method to run: basic or local",
    )
    p.add_argument("--output-key", type=str, default="query_context.json", help="Key/filename to save context json into storage")
    p.add_argument("--save-response", action="store_true", help="Also save the textual response to storage as .txt")
    p.add_argument("--verbose", action="store_true")
    return p.parse_args()


def main(args: argparse.Namespace) -> None:
    root = Path(args.root).resolve()
    cli_overrides = {}

    config = load_config(root, args.config, cli_overrides)

    # Create storage object from config.output (same as CLI uses)
    storage = create_storage_from_config(config.output)

    response = None
    context_data: Any = {}

    # Choose method and load required tables
    if args.method == "basic":
        # Load text_units table required for basic_search
        try:
            text_units = asyncio.run(load_table_from_storage("text_units", storage))
        except Exception as e:
            logger.error("Could not load text_units from storage: %s", e)
            raise

        # Run the basic_search API to get response and context_data
        try:
            response, context_data = asyncio.run(
                api.basic_search(
                    config=config,
                    text_units=text_units,
                    query=args.query,
                    callbacks=None,
                    verbose=args.verbose,
                )
            )
        except Exception as e:
            logger.exception("Error running basic_search: %s", e)
            raise

    elif args.method == "local":
        # Local search needs: entities, communities, community_reports, text_units, relationships
        try:
            entities = asyncio.run(load_table_from_storage("entities", storage))
            communities = asyncio.run(load_table_from_storage("communities", storage))
            community_reports = asyncio.run(load_table_from_storage("community_reports", storage))
            text_units = asyncio.run(load_table_from_storage("text_units", storage))
            relationships = asyncio.run(load_table_from_storage("relationships", storage))
        except Exception as e:
            logger.error("Could not load one of required tables for local search: %s", e)
            raise

        # covariates are optional
        covariates = None
        try:
            covariates = asyncio.run(load_table_from_storage("covariates", storage))
        except Exception:
            covariates = None

        # Run the local_search API to get response and context_data
        try:
            response, context_data = asyncio.run(
                api.local_search(
                    config=config,
                    entities=entities,
                    communities=communities,
                    community_reports=community_reports,
                    text_units=text_units,
                    relationships=relationships,
                    covariates=covariates,
                    community_level=0,
                    response_type="default",
                    query=args.query,
                    callbacks=None,
                    verbose=args.verbose,
                )
            )
        except Exception as e:
            logger.exception("Error running local_search: %s", e)
            raise

    # Prepare serializable version of context_data
    try:
        serializable = reformat_context_data(context_data) if isinstance(context_data, dict) else context_data
    except Exception:
        # Fallback: try to dump whatever it is
        serializable = context_data

    # Save context JSON to storage
    payload = json.dumps(serializable, ensure_ascii=False, indent=2)

    async def _save():
        # storage.set accepts bytes or text - implementations support both
        await storage.set(args.output_key, payload)
        if args.save_response:
            await storage.set(args.output_key + ".response.txt", str(response))

    asyncio.run(_save())

    print(f"Saved context_data to storage key: {args.output_key}")
    if args.save_response:
        print(f"Saved response to storage key: {args.output_key}.response.txt")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    args = parse_args()
    main(args)
