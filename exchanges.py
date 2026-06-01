"""
Ecoinvent Mock Code Review Exercise
====================================
Context: This module is part of a data pipeline that loads life cycle inventory
(LCI) exchanges from a CSV, validates them, and writes a summary report.

Your task:
  1. Read the code carefully.
  2. List every issue you find — bugs, OOP violations, error handling problems,
     design smells, logging issues, testing concerns.
  3. For each issue: explain WHY it's a problem and suggest a concrete fix.
  4. Identify at least one design-level improvement (not just line fixes).

There are approximately 15 issues of varying severity.
"""

import logging
import pandas as pd
import json

logger = logging.getLogger(__name__)


# ──────────────────────────────────────────────
# Models
# ──────────────────────────────────────────────

class Exchange:
    valid_units = ["kg", "MJ", "m3", "kWh"]

    def __init__(self, activity_id, amount, unit, compartment=None):
        self.activity_id = activity_id
        self.amount = amount
        self.unit = unit
        self.compartment = compartment
        self.validated = False

    def validate(self):
        if self.amount < 0:
            print(f"[ERROR] Negative amount for {self.activity_id}")
            return False
        if self.unit not in self.valid_units:
            print(f"[ERROR] Invalid unit {self.unit}")
            return False
        self.validated = True
        return True


class TechnosphereExchange(Exchange):
    def __init__(self, activity_id, amount, unit):
        super().__init__(activity_id, amount, unit)
        self.type = "technosphere"

    def to_dict(self):
        return {
            "activity_id": self.activity_id,
            "amount": self.amount,
            "unit": self.unit,
            "type": self.type
        }


class BiosphereExchange(Exchange):
    def __init__(self, activity_id, amount, unit, compartment):
        super().__init__(activity_id, amount, unit, compartment)
        self.type = "biosphere"

    def validate(self):
        if not self.compartment:
            print(f"[ERROR] Missing compartment for {self.activity_id}")
            return False
        return super().validate()

    def to_dict(self):
        return {
            "activity_id": self.activity_id,
            "amount": self.amount,
            "unit": self.unit,
            "compartment": self.compartment,
            "type": self.type
        }


class ExchangeFactory:
    """Constructs Exchange objects from raw DataFrame rows."""

    @staticmethod
    def from_row(row) -> Exchange:
        if row.type == "technosphere":
            return TechnosphereExchange(row.activity_id, row.amount, row.unit)
        elif row.type == "biosphere":
            return BiosphereExchange(row.activity_id, row.amount, row.unit, row.compartment)
        else:
            raise ValueError(f"Unknown exchange type: {row.type!r}")

# ──────────────────────────────────────────────
# Processor
# ──────────────────────────────────────────────

class ExchangeProcessor:

    def __init__(self, filepath: str) -> None:
        self.filepath = filepath
        self.exchanges: list[Exchange] = []
        self.errors: list[tuple] = []

    def load(self) -> None:
        try:
            df = pd.read_csv(self.filepath)
        except FileNotFoundError:
            raise FileNotFoundError(f"Input file not found: {self.filepath!r}")
        except pd.errors.ParserError as e:
            raise ValueError(f"Could not parse CSV at {self.filepath!r}") from e

        for row in df.itertuples(index=False):  # fix 4: was iterrows()
            try:
                exchange = ExchangeFactory.from_row(row)  # fix 5: factory extracted
                self.exchanges.append(exchange)
            except ValueError as e:
                logger.warning("Skipping row — %s", e)  # fix 6: was print(), no continue

    def validate_all(self) -> None:
        for exchange in self.exchanges:
            try:
                exchange.validate()
            except Exception as e:
                logger.exception("Unexpected error validating %r: %s", exchange, e)  # fix 7: no silent swallow
                self.errors.append((exchange, e))

    def get_summary(self) -> dict[str, int]:
        total = len(self.exchanges)
        validated = sum(1 for e in self.exchanges if e.validated)  # fix 8: no list comprehension
        return {"total": total, "validated": validated}

    def write_report(self, output_path: str) -> None:
        results = [e.to_dict() for e in self.exchanges if e.validated]  # fix 9: polymorphic, no isinstance

        with open(output_path, "w") as f:  # fix 10: context manager
            json.dump(results, f)

        logger.info("Report written to %s (%d records)", output_path, len(results))  # fix 11: informative message


# ──────────────────────────────────────────────
# Entry point
# ──────────────────────────────────────────────

def run(filepath, output_path):
    processor = ExchangeProcessor(filepath)
    processor.load()
    processor.validate_all()
    summary = processor.get_summary()
    print(summary)
    processor.write_report(output_path)