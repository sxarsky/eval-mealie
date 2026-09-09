# Recipe Notes

Status: Accepted

## 1. Scope

This document specifies the behaviour of recipe notes: the free-form `notes`
entries attached to a recipe and exchanged through the recipe API
(`GET`/`PUT`/`PATCH /api/recipes/{slug}`) and edited on the recipe page.

The key words MUST, MUST NOT, SHOULD and MAY are to be interpreted as
described in RFC 2119.

## 2. Data model

A recipe carries an ordered list of notes. Each note has:

| Field   | Type   | Constraints                          |
|---------|--------|--------------------------------------|
| `title` | string | required                             |
| `text`  | string | required, at most 255 characters     |

Notes are stored and returned in the order they were submitted.

## 3. Length limit

3.1. The `text` of a note MUST NOT exceed 255 characters. The limit is
measured in Unicode code points, not bytes.

3.2. A `text` of exactly 255 characters is valid and MUST be accepted.

3.3. The limit applies to every note in the list, on every write path that
accepts recipe notes (`PUT /api/recipes/{slug}`, `PATCH /api/recipes/{slug}`,
and the bulk `PUT`/`PATCH /api/recipes` variants).

3.4. The limit is enforced by the API layer. Clients SHOULD enforce the same
limit in the editor so that users are not surprised by a rejected save; the
recipe page editor displays a character counter and does not accept input
beyond 255 characters.

## 4. Validation failure

4.1. When any note in a request exceeds the limit, the API MUST reject the
whole request with HTTP `422 Unprocessable Entity` and MUST NOT persist any
part of the update.

4.2. The response body MUST use the application's standard validation error
response for `422`, identifying the offending `notes[].text` field.

4.3. Notes that are within the limit are not affected by a rejected request:
the recipe remains as it was before the request.

## 5. Reading notes

5.1. `GET /api/recipes/{slug}` MUST return notes exactly as stored, including
their `title` and `text`, in submission order.

5.2. Reading notes never applies truncation.

## 6. Non-goals

- This document does not specify note formatting. Note text MAY contain
  Markdown; rendering is a client concern.
- No limit is specified for `title` beyond it being required.
