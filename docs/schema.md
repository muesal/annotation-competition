# Main Tables

## User

This seems to be as simple as this:

| Column | Type | Notes |
| ------ | ------- | ------- |
| **ID** | **int** | **unsigned, primary** |
| username | string | (never `NULL` |
| score | int | unsigned (default `0`, never `NULL`) |
| auth token/cookie | string | (may be we need an expire date?) |


## Tag

Tags are also quite simple:

| Column | Type | Notes |
| ------ | ------- | ------- |
| **ID** | **int** | **unsigned, primary** |
| name | string | unique (never `NULL`) |

### Tag with synonym

Or maybe we can flag synonyms like this in the future?

| Column | Type | Notes |
| ------ | ------- | ------- |
| **ID** | **int** | **unsigned, primary** |
| name | string | unique (never `NULL`) |
| *synonym* | *int* | *unsigned (reference to similar tag id)* |

Do we need reverse lookups for synonyms?

## Image

| Column | Type | Notes |
| ------ | ------- | ------- |
| **ID** | **int** | **unsigned, primary** |
| filename | string | unique (never `NULL`) |
| skips | int | unsigned (default `0`, never `NULL`) |

The status has to be calculated.

# Relation tables

images and tags have `M*N` relations:

## Image_Tag (classic)

| Column | Type | Notes |
| ------ | ------- | ------- |
| *image ID* | *int* | *unsigned, foregin* |
| *tag ID* | *int* | *unsigned, foregin* |
| frequency | int | unsigned (default `0`, never `NULL`) |
| quality/verified successful | int | unsigned (default `0`, never `NULL`) |
| total verifications | int | unsigned (default `0`, never `NULL`) |

## seen

| Column | Type | Notes |
| ------ | ------- | ------- |
| *image ID* | **int** | **unsigned, foregin** |
| *user ID* | *int* | *unsigned, foregin* |

unique combination