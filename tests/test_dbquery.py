import pytest
from typing import Any
from unittest.mock import Mock, patch
from datetime import date
from db.db import DatabaseService, PackageType
from app.app_helpers import app_config
from pandas import DataFrame

# Archetype:
# @pytest.mark.parametrize("test_case", database_test_cases)
# def test_verb_adjective(test_case, database_access):
#     # Arrange
#     sut = database_access
#     df = sut.populate(123, date(2023, 10, 1), test_case)
#     expected = df # calculate value expected

#     # Act
#     result = sut.method

#     # Assert
#     assert dataframes_equivalent(result, expected)

# TODO add snapshot
# pytest --snapshot-update #when necessary

# This pair of dates is a 1 year span to go with the database test cases
current_date = app_config.today()
test_start_date = date(2022,10,1)
test_end_date =  date(2023,9,30)

database_test_cases = [
    [
        (PackageType.BIOC, 'affydata', '2023-08-01')
    ],
    [
        (PackageType.BIOC, 'affy', '2023-09-01'), 
        (PackageType.BIOC, 'affydata', '2023-08-01')
    ],
    [
        (PackageType.BIOC, 'affy', '2023-09-01'), 
        (PackageType.BIOC, 'affydata', '2023-08-01'),
        (PackageType.ANNOTATION, 'BSgenome.Hsapiens.UCSC.hg38', '2019-01-01')
    ]
]

def dataframes_equivalent(a: DataFrame, b:DataFrame) -> bool:
    # Need to deal with empty dataframes seperatly due to equals semantics for empty dataframes
    if len(a) == 0 and len(b) == 0:
        return True
    return a.reset_index(drop=True).equals(b.reset_index(drop=True))

@pytest.mark.parametrize("test_case", database_test_cases)
def test_populate_database_one_package(snapshot, test_case: Any, database_access: DatabaseService):
    # Arrange
    sut = database_access
    expected = sut.populate(123, date(2023, 10, 1), test_case)
    
    # Act
    result = sut.select()

    # Assert
    assert result.equals(expected)
    
@pytest.mark.parametrize("test_case", database_test_cases)
def test_get_package_names(test_case: Any, database_access: DatabaseService):
    # Arrange
    sut = database_access
    df = sut.populate(123, date(2023, 10, 1), test_case)
    expected = df[['package']].drop_duplicates().sort_values(by='package')

    # Act
    result = sut.get_package_names()

    # Assert

    assert dataframes_equivalent(result, expected)
    

@pytest.mark.parametrize("test_case", database_test_cases)
def test_get_download_counts_for_category(test_case: Any, database_access: DatabaseService):
    # Arrange
    sut = database_access
    df = sut.populate(123, date(2023, 10, 1), test_case)
    # we will be looking for all rows 
    expected = df[df['category'] == PackageType.BIOC].sort_values(by=['package', 'date'])

    # Act
    result = sut.get_download_counts(PackageType.BIOC)

    # Assert
    assert dataframes_equivalent(result, expected)

@pytest.mark.parametrize("test_case", database_test_cases)
def test_get_download_counts_for_pacakge(test_case: Any, database_access: DatabaseService):
    # Arrange
    sut = database_access
    df = sut.populate(123, date(2023, 10, 1), test_case)
    # we will be looking for all rows 
    expected = df[(df['category'] == PackageType.BIOC) & (df['package'] == 'affy')].sort_values(by=['package', 'date'])

    # Act
    result = sut.get_download_counts(PackageType.BIOC, 'affy')

    # Assert
    assert dataframes_equivalent(result, expected)

@pytest.mark.parametrize("test_case", database_test_cases)
def test_get_download_counts_for_pacakge_year(test_case: Any, database_access: DatabaseService):
    # Arrange
    sut = database_access
    df = sut.populate(123, date(2023, 10, 1), test_case)
    # we will be looking for all rows 
    expected = df[(df['category'] == PackageType.ANNOTATION) & 
                (df['package'] == 'BSgenome.Hsapiens.UCSC.hg38') &
                ([d.year == 2021 for d in df['date']])].sort_values(by=['package', 'date'])

    # Act
    result = sut.get_download_counts(PackageType.ANNOTATION, 'BSgenome.Hsapiens.UCSC.hg38', 2021)

    # Assert
    assert dataframes_equivalent(result, expected)



@pytest.mark.parametrize("test_case", database_test_cases)
def test_get_scores_for_category_get(test_case: Any, database_access: DatabaseService):
    # Arrange
    sut = database_access
    df = sut.populate(123, date(2023, 10, 1), test_case)
    
    
    expected = df[(df['category'] == PackageType.ANNOTATION) & 
                (df['package'] == 'BSgenome.Hsapiens.UCSC.hg38') &
                ([d.year == 2023 for d in df['date']])].sort_values(by=['package', 'date'])

    # Act
    result = sut.get_download_scores_for_category(PackageType.BIOC)

    # Assert
    # TODO establish appropriate assert
#    assert dataframes_equivalent(result, expected)
    assert True


@pytest.mark.parametrize("test_case", database_test_cases)
def test_get_score_for_package_get(test_case: Any, database_access: DatabaseService):
    # Arrange
    sut = database_access
    df = sut.populate(123, date(2023, 10, 1), test_case)
    package = df.at[df.index[-1], 'package']
    score = df[(df.package == package) & (df['date'] >= test_start_date) & (df['date'] <= test_end_date)].ip_count.sum() // 12
    expected = DataFrame({'package': [package], 'score': [score] })

    # Act
    result = sut.get_download_score_for_package(package)

    # Assert
    assert dataframes_equivalent(result, expected)
    