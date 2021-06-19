"""Test data structures."""

from mrgf import GovernaceFramework

SAMPLE_GFW = {
    "@context": [
        "https://github.com/hyperledger/aries-rfcs/blob/master/concepts/"
        "0430-machine-readable-governance-frameworks/context.jsonld"
    ],
    "name": "sample",
    "version": "0.1",
    "data_uri": "some location",
    "description": "sample",
    "roles": ["one", "two"],
    "define": [
        {"name": "entity", "id": "DID here"},
        {"name": "entity-test", "id": "DID here"},
        {
            "name": "approved-issuer-1",
            "id": "insert approved issuer 1 main net DID here",
        },
        {
            "name": "approved-issuer-2",
            "id": "insert approved issuer 2 main net DID here",
        },
        {"name": "approved-schema-1", "id": "schema-id-1"},
        {"name": "approved-schema-2", "id": "schema-id-2"},
    ],
    "privileges": [
        {
            "name": "privilege-issuers",
            "description": "Able to handle credentials from defined issuers.",
            "uri": "",
            "value": [
                "entity",
                "entity-test",
                "approved-issuer-1",
                "approved-issuer-2",
            ],
        },
        {
            "name": "privilege-schemas",
            "uri": "",
            "description": "Schemas approved for use by white label partners.",
            "value": ["approved-schema-1", "approved-schema-2"],
        },
        {
            "name": "created-connections",
            "uri": "",
            "description": "Access to connections created by this partner.",
        },
        {"name": "all", "uri": "", "description": "Access to everything."},
    ],
    "rules": [
        {
            "grant": ["privilege-issuers", "privilege-schemas", "connections-created"],
            "when": {"roles": "one"},
        },
        {"grant": ["all"], "when": {"roles": "two"}},
    ],
}


def test_parse_gfw():
    gfw = GovernaceFramework(**SAMPLE_GFW)
    assert gfw.version == "0.1"
    assert gfw.privileges[0].name == "privilege-issuers"
    assert gfw.define[0].name == "entity"
