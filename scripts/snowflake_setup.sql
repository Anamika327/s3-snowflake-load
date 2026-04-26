-- Snowflake Database, Schema, and External Stage Configuration for S3 Integration

-- Create Database
CREATE DATABASE IF NOT EXISTS my_database;

-- Create Schema
CREATE SCHEMA IF NOT EXISTS my_database.my_schema;

-- Create External Stage
CREATE STAGE my_external_stage
URL = 's3://my-bucket-path'
CREDENTIALS = (AWS_KEY = '<AWS_KEY>' AWS_SECRET = '<AWS_SECRET>')
FILE_FORMAT = (TYPE = 'CSV');

-- Note: Replace '<AWS_KEY>' and '<AWS_SECRET>' with your actual AWS credentials.