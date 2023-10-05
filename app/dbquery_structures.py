"""
Module Name: dbquery_structures

Description:
    Data structures for bioc_package_stats queries

Classes:
    - QueryRequest: Represents a query request, encapsulating query types and keys.
    - QueryResponse: Represents the status and results returned from a query.
    - ResultEntry: Represents a single entry in a query result.

Usage:
    from data_structures import DbQueryRequest, DbQueryResponse, DbResultEntry
    request = QueryRequest('query_type', 'package_type', 'package_name', 'year')
    response = QueryResponse('status', [...])
    
Additional Information:
    none
"""
# TODO camel -> underbar

from collections import namedtuple
from enum import Enum, auto

class QueryRequestType(Enum):
    PACKAGE_SCORES = auto()     # Return package names and scores, one row for each package
    PACKAGE_COUNTS = auto()     # Return package names and counts
    PACKAGE_NAMES = auto()

class PackageType(Enum):
    BIOC = "Software"
    EXPERIMENT = "Experiment"
    ANNOTATION = "Annotation"
    WORKFLOW = "Wowrkflow"
    
from enum import Enum, auto

class DataRetrievalStatus(Enum):
    SUCCESS = auto()
    NOT_FOUND = auto()
    ERROR = auto()
    TIMEOUT = auto()

"""
Represents a query request, including query type and up to three keys.
        query_type - See QueryRequestType enum
        package_type - ASee PackageType enum
        package_name - If an empty string, then all packages in the specified package_type.
                        Otherwise, select the specific package.
        year - If an empty string, then all the data for the 
                        specified package_type and package_name criteria
                        Otherwise a 4 digit string, e.g. '2023'
"""
DbQueryRequest = namedtuple("DbQueryRequest", ["query_type", "package_type", "package_name", "year"])
"""
Represents the response status and result set.
        status - See DataRetrievalStatus enum
        result - An array of results, see DbResultEntry
"""
DbQueryResponse = namedtuple("DbQueryResponse", ["status", "result"])

"""
Represents a single entry in the result set, containing a date and a count.
    date -  Date in the format YYYY-MM-DD or empty string if not present
    isYearly - If false, then the date denotes the one month date span
                which contains the given date.
               If true, then the date denotes the year.
               Example: date='2021-06-01'
                    isYearly=false => date span: 2021-06-01:2021-06-30
                    isYearly=true => date span: 2021-06-01:2022-05-31
                UniqueIpCount, int, the innique IP count for the period
                downloadCount, int, the download count 
"""
DbResultEntry = namedtuple("DbResultEntry", ["package_name", "date", "isYearly", "uniqueIpCount", "downloadCount"])
