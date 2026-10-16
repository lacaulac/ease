# EASE: **E**PITA **A**uriga **S**chedule **E**xporter

## How to

### Using pipx (recommended)

Install EASE with pipx:

```
pipx install https://github.com/lacaulac/ease/releases/latest/download/ease-py3-none-any.whl
```

You can then set-up EASE by running `ease-setup`, and use EASE by running `ease`. Updates can then be run using `pipx update ease`

### Using `uv` and virtual environments

This was meant to be run with [`uv`](https://docs.astral.sh/uv/getting-started/installation/); it allows seamless use of virtual environments and handles Python versions and dependency installation on its own. You can install it on GNU/Linux systems with the following:

```sh
curl -LsSf https://astral.sh/uv/install.sh | sh
```

You can then set up EASE:

```sh
uv run setup
```

**Warning : your password will be stored in plaintext**

Finally, you can just run EASE anytime you want an export of your calendar :)

```sh
uv run ease
```

## General algorithm

1. Connects to auriga.epita.fr
2. Gets redirected into oblivion for a bit
3. Inputs credentials (you can do that manually too)
4. Logs in
5. Hijacks the auth token
6. Exports the calendar's JSON for the current year
7. Converts it into a .ics file
8. ???
9. Profit


## Miscellaneous

### JSON Schema

Yeah, those exports are *big*

```
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "title": "Interventions Export",
  "type": "object",
  "required": ["interventions", "unavailabilities"],
  "properties": {
    "interventions": {
      "type": "array",
      "items": {
        "$ref": "#/$defs/intervention"
      }
    },
    "unavailabilities": {
      "type": "array"
    }
  },
  "$defs": {
    "localizedText": {
      "type": "object",
      "additionalProperties": {
        "type": ["string", "null"]
      }
    },

    "person": {
      "type": "object",
      "required": ["id", "currentFirstName", "currentLastName"],
      "properties": {
        "id": {
          "type": "integer"
        },
        "currentFirstName": {
          "type": "string"
        },
        "currentLastName": {
          "type": "string"
        }
      }
    },

    "activityType": {
      "type": "object",
      "required": ["id", "code", "caption"],
      "properties": {
        "id": {
          "type": "integer"
        },
        "code": {
          "type": "string"
        },
        "caption": {
          "$ref": "#/$defs/localizedText"
        }
      }
    },

    "interventionReference": {
      "type": "object",
      "properties": {
        "id": {
          "type": "integer"
        },
        "accountedDuration": {
          "type": "integer"
        },
        "actualDuration": {
          "type": "integer"
        },
        "startDateTime": {
          "type": "string",
          "format": "date-time"
        },
        "endDateTime": {
          "type": "string",
          "format": "date-time"
        },
        "additionalRemarks": {
          "$ref": "#/$defs/localizedText"
        },
        "customAttributes": {
          "type": "object"
        }
      },
      "required": ["id"]
    },

    "interventionInstructor": {
      "type": "object",
      "required": ["id", "person"],
      "properties": {
        "id": {
          "type": "integer"
        },
        "person": {
          "$ref": "#/$defs/person"
        }
      }
    },

    "pedagogicalUnit": {
      "type": "object",
      "required": ["id", "code"],
      "properties": {
        "id": {
          "type": "integer"
        },
        "code": {
          "type": "string"
        },
        "caption": {
          "$ref": "#/$defs/localizedText"
        },
        "externalCode": {
          "type": "object",
          "properties": {
            "key": {
              "type": "string"
            }
          }
        },
        "customAttributes": {
          "type": "object"
        }
      }
    },

    "population": {
      "type": "object",
      "required": ["id", "code"],
      "properties": {
        "id": {
          "type": "integer"
        },
        "code": {
          "type": "string"
        },
        "caption": {
          "$ref": "#/$defs/localizedText"
        },
        "externalCode": {
          "type": "object",
          "properties": {
            "key": {
              "type": "string"
            }
          }
        },
        "populationType": {
          "type": "object"
        }
      }
    },

    "program": {
      "type": "object",
      "required": ["id", "code"],
      "properties": {
        "id": {
          "type": "integer"
        },
        "code": {
          "type": "string"
        },
        "caption": {
          "$ref": "#/$defs/localizedText"
        }
      }
    },

    "resourceType": {
      "type": "object",
      "required": ["id", "code"],
      "properties": {
        "id": {
          "type": "integer"
        },
        "code": {
          "type": "string"
        },
        "caption": {
          "$ref": "#/$defs/localizedText"
        },
        "isManagingConflictsEnabled": {
          "type": "boolean"
        }
      }
    },

    "resource": {
      "type": "object",
      "required": ["id", "code"],
      "properties": {
        "id": {
          "type": "integer"
        },
        "code": {
          "type": "string"
        },
        "caption": {
          "$ref": "#/$defs/localizedText"
        },
        "description": {
          "$ref": "#/$defs/localizedText"
        },
        "floor": {
          "type": "integer"
        },
        "examCapacity": {
          "type": "integer"
        },
        "totalCapacity": {
          "type": "integer"
        },
        "isAccessibleForDisablePeople": {
          "type": "boolean"
        },
        "isRoom": {
          "type": "boolean"
        },
        "resourceType": {
          "$ref": "#/$defs/resourceType"
        }
      }
    },

    "attendanceStatus": {
      "type": "object",
      "required": ["id", "code"],
      "properties": {
        "id": {
          "type": "integer"
        },
        "code": {
          "type": "string"
        },
        "caption": {
          "$ref": "#/$defs/localizedText"
        }
      }
    },

    "participation": {
      "type": "object",
      "required": [
        "id",
        "absenceExcused",
        "isRemote",
        "person"
      ],
      "properties": {
        "id": {
          "type": "integer"
        },
        "absenceExcused": {
          "type": "boolean"
        },
        "absenceReason": {
          "type": "object"
        },
        "attendanceStatus": {
          "$ref": "#/$defs/attendanceStatus"
        },
        "automaticRegistrationStatus": {
          "$ref": "#/$defs/attendanceStatus"
        },
        "participationStatus": {
          "type": "object"
        },
        "isRemote": {
          "type": "boolean"
        },
        "person": {
          "$ref": "#/$defs/person"
        }
      }
    },

    "timezone": {
      "type": "object",
      "required": [
        "id",
        "code",
        "name"
      ],
      "properties": {
        "id": {
          "type": "integer"
        },
        "abbreviation": {
          "type": "string"
        },
        "code": {
          "type": "string"
        },
        "description": {
          "type": "string"
        },
        "dst": {
          "type": "boolean"
        },
        "name": {
          "type": "string"
        },
        "utcOffset": {
          "type": "number"
        },
        "utcOffsetWithDst": {
          "type": "number"
        }
      }
    },

    "interventionStatus": {
      "type": "object",
      "required": ["id", "code"],
      "properties": {
        "id": {
          "type": "integer"
        },
        "code": {
          "type": "string"
        },
        "caption": {
          "$ref": "#/$defs/localizedText"
        },
        "isAccessAttendanceListsDisabled": {
          "type": "boolean"
        },
        "isBillable": {
          "type": "boolean"
        },
        "isDisplayedInSchedules": {
          "type": "boolean"
        },
        "isHoursTaughtCountedInPrc": {
          "type": "boolean"
        },
        "isHoursTaughtCountedInWorkloadPlan": {
          "type": "boolean"
        },
        "isHoursTaughtExportedToPayroll": {
          "type": "boolean"
        },
        "isInstructorConflictsEnabled": {
          "type": "boolean"
        },
        "isLearnerConflictsEnabled": {
          "type": "boolean"
        },
        "isPartOfAttendanceLists": {
          "type": "boolean"
        },
        "isResourceConflictsEnabled": {
          "type": "boolean"
        },
        "toSchedule": {
          "type": "boolean"
        }
      }
    },

    "intervention": {
      "type": "object",
      "required": [
        "id",
        "activityType",
        "actualDuration",
        "startDateTime",
        "endDateTime",
        "isExam"
      ],
      "properties": {
        "id": {
          "type": "integer"
        },
        "activityType": {
          "$ref": "#/$defs/activityType"
        },
        "actualDuration": {
          "type": "integer"
        },
        "startDateTime": {
          "type": "string",
          "format": "date-time"
        },
        "endDateTime": {
          "type": "string",
          "format": "date-time"
        },
        "field": {
          "type": "object"
        },
        "isExam": {
          "type": "boolean"
        },
        "interventionInstructors": {
          "type": "array",
          "items": {
            "$ref": "#/$defs/interventionInstructor"
          }
        },
        "interventionPedagogicalUnits": {
          "type": "array"
        },
        "interventionPopulations": {
          "type": "array"
        },
        "interventionPrograms": {
          "type": "array"
        },
        "interventionResources": {
          "type": "array"
        },
        "interventionStatus": {
          "$ref": "#/$defs/interventionStatus"
        },
        "participations": {
          "type": "array",
          "items": {
            "$ref": "#/$defs/participation"
          }
        },
        "timezone": {
          "$ref": "#/$defs/timezone"
        }
      }
    }
  }
}

```
