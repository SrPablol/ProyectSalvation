"""
Reads leads from an Apollo.io CSV export.

Apollo CSV columns (standard export):
  First Name, Last Name, Title, Company, Email, Website, LinkedIn URL,
  # Employees, Industry, City, State, Country, ...
"""

import pandas as pd
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Lead:
    first_name: str
    last_name: str
    email: str
    title: str
    company: str
    website: str
    industry: str = ""
    employees: str = ""
    city: str = ""
    country: str = ""
    linkedin: str = ""
    extra: dict = field(default_factory=dict)

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}".strip()

    def __str__(self) -> str:
        return f"{self.full_name} ({self.title}) @ {self.company} <{self.email}>"


# Map CSV column names → Lead field names
# Supports Apollo standard export (title case) and lowercase_underscore format
COLUMN_MAP = {
    # Apollo standard export
    "First Name": "first_name",
    "Last Name": "last_name",
    "Email": "email",
    "Title": "title",
    "Company Name": "company",
    "Company": "company",
    "Website": "website",
    "Industry": "industry",
    "# Employees": "employees",
    "City": "city",
    "Country": "country",
    "Person Linkedin Url": "linkedin",
    "LinkedIn URL": "linkedin",
    # Lowercase underscore format (leads-100.csv and similar exports)
    "first_name": "first_name",
    "last_name": "last_name",
    "email": "email",
    "title": "title",
    "company": "company",
    "domain": "website",        # fallback — overwritten by "website" if present
    "website": "website",
    "industry": "industry",
    "employees": "employees",
    "city": "city",
    "country": "country",
    "linkedin_url": "linkedin",
}


def read_csv(path: str) -> list[Lead]:
    df = pd.read_csv(path, dtype=str).fillna("")
    leads = []

    for _, row in df.iterrows():
        kwargs = {}
        for csv_col, field_name in COLUMN_MAP.items():
            val = row.get(csv_col, "").strip()
            if val:
                kwargs[field_name] = val

        # Skip rows without email
        if not kwargs.get("email"):
            continue

        lead = Lead(**kwargs)
        leads.append(lead)

    print(f"  Cargados {len(leads)} leads desde '{path}'")
    return leads
