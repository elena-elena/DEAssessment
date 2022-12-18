import pandas as pd
import os

from localapp.etl.transform import split_string_column, clean_string_field


def test_split_string_col():
	test_input = pd.DataFrame({'id':[1, 2, 3, 4, 5], 'message':['1,lorem,ipsum', '2,foo,bar', '3,xyz,abc', '4,the,fox', '5,test,words']})
	test_header = ['id2', 'col1', 'col2']
	actual = split_string_column(test_input, 'message', test_header)
	expected = pd.DataFrame({'id2': ['1','2','3','4','5'], 'col1': ['lorem','foo', 'xyz', 'the', 'test'], 'col2': ['ipsum', 'bar', 'abc', 'fox', 'words']})
	
	assert actual.equals(expected)


def test_clean_string_field():
	test_input = pd.Series(['1,as.f,hhh', '2,$gfj,kk#j@9'])
	actual = clean_string_field(test_input, '[^0-9a-zA-Z,.]+', ' ')
	expected = pd.Series(['1,as.f,hhh', '2, gfj,kk j 9'])
	assert actual.equals(expected)