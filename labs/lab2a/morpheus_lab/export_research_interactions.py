"""Export pseudonymous Research Mode v1 interaction events to CSV."""
from morpheus_lite.research_mode import export_csv

if __name__ == "__main__":
    count = export_csv()
    print(f"Exported {count} research events to exports/research_events.csv")
