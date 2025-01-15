def get_fake_db() -> dict:
    return {
        'archived': False,
        'cover': {
            'external': {
                'url': 'https://images.unsplash.com/photo-1471506480208-91b3a4cc78be?ixlib=rb-4.0.3&q=85&fm=jpg&crop=entropy&cs=srgb'
            },
            'type': 'external'
        },
        'created_by': {
            'id': 'b35f54bf-0b56-45c2-badf-b107f94a79d3',
            'object': 'user'
        },
        'created_time': '2024-09-07T14:37:00.000Z',
        'description': [],
        'icon': {
            'file': {
                'expiry_time': '2025-01-14T23:24:38.096Z',
                'url': 'https://prod-files-secure.s3.us-west-2.amazonaws.com/5f8cbff8-587c-40dc-b000-881bd747e0a2/16cd48d4-264e-4737-919c-dfa23d45304...=3600&X-Amz-Signature=cc080e480b43e85d4587d3671d31cce9767d9c0f0e7c2b7aa36833d3cd886027&X-Amz-SignedHeaders=host&x-id=GetObject'
            },
            'type': 'file'
        },
        'id': '381d8720-f394-468e-a63d-9f75aec3064d',
        'in_trash': False,
        'is_inline': False,
        'last_edited_by': {
            'id': 'b35f54bf-0b56-45c2-badf-b107f94a79d3',
            'object': 'user'
        },
        'last_edited_time': '2025-01-14T05:05:00.000Z',
        'object': 'database',
        'parent': {
            'block_id': 'ac7ce652-36bc-4b98-9dff-8df172c34980',
            'type': 'block_id'
        },
        'properties': {
            'AE:AN': {
                'formula': {
                    'expression': 'round({{notion:block_property:gGRs:00000000-0000-0000-0000-000000000000:5f8cbff8-587c-40dc-b000-881bd747e0a2}})+":"+round({{notion:block_property:U%5C%3Eb:00000000-0000-0000-0000-000000000000:5f8cbff8-587c-40dc-b000-881bd747e0a2}})'
                },
                'id': 'IrNS',
                'name': 'AE:AN',
                'type': 'formula'
            },
            'Activity Name': {
                'id': 'title',
                'name': 'Activity Name',
                'title': {},
                'type': 'title'
            },
            'Activity Type': {
                'id': 'qXF_',
                'name': 'Activity Type',
                'select': {
                    'options': [
                        {
                            'color': 'default',
                            'description': None,
                            'id': '4872da0a-43f6-42f0-a60f-c245d60d06e4',
                            'name': 'Cycling'
                        },
                        {
                            'color': 'default',
                            'description': None,
                            'id': 'c6205215-4ca8-4f48-a64e-42f80e5ffa87',
                            'name': 'Hiking'
                        },
                        {
                            'color': 'brown',
                            'description': None,
                            'id': 'f66064e7-1198-4a9e-9bb4-5d80840343df',
                            'name': 'Other'
                        },
                        {
                            'color': 'pink',
                            'description': None,
                            'id': '548eb537-b58a-4485-ad64-749e35e79375',
                            'name': 'Rowing'
                        },
                        {
                            'color': 'orange',
                            'description': None,
                            'id': 'fa274568-2327-4df9-9007-0d2847a60a3d',
                            'name': 'Running'
                        },
                        {
                            'color': 'pink',
                            'description': None,
                            'id': 'd37c1c88-912c-455b-938e-76f7dfaee940',
                            'name': 'Stretching'
                        },
                        {
                            'color': 'purple',
                            'description': None,
                            'id': 'fb82c99f-32aa-4134-919b-b4f98dc071d5',
                            'name': 'Walking'
                        },
                        {
                            'color': 'gray',
                            'description': None,
                            'id': '8f4017af-f7f3-4e94-aa3b-827992541a53',
                            'name': 'Relaxation'
                        },
                        {
                            'color': 'red',
                            'description': None,
                            'id': 'e5be251e-d64e-49e0-9c22-169298d8a39b',
                            'name': 'Cardio'
                        },
                        {
                            'color': 'gray',
                            'description': None,
                            'id': 'e3233c22-4569-400d-bf24-730032fc98ae',
                            'name': 'Strength'
                        },
                        {
                            'color': 'blue',
                            'description': None,
                            'id': '67cbc3c7-3d3a-453e-aac6-dff37a54c1c1',
                            'name': 'Yoga/Pilates'
                        }
                    ]
                },
                'type': 'select'
            },
            'Aerobic': {
                'id': 'gGRs',
                'name': 'Aerobic',
                'number': {
                    'format': 'number'
                },
                'type': 'number'
            },
            'Aerobic Effect': {
                'id': '%40ofX',
                'name': 'Aerobic Effect',
                'select': {
                    'options': [
                        {
                            'color': 'red',
                            'description': None,
                            'id': 'rVCX',
                            'name': 'Overreaching'
                        },
                        {
                            'color': 'green',
                            'description': None,
                            'id': 'FJpb',
                            'name': 'Highly Impacting'
                        },
                        {
                            'color': 'blue',
                            'description': None,
                            'id': 'PfdA',
                            'name': 'Impacting'
                        },
                        {
                            'color': 'orange',
                            'description': None,
                            'id': '@mJg',
                            'name': 'Maintaining'
                        },
                        {
                            'color': 'yellow',
                            'description': None,
                            'id': 'qgQC',
                            'name': 'Some Benefit'
                        },
                        {
                            'color': 'brown',
                            'description': None,
                            'id': '5398079d-731f-4ebb-9365-b6945746d080',
                            'name': 'Recovery'
                        },
                        {
                            'color': 'gray',
                            'description': None,
                            'id': 'JPja',
                            'name': 'No Benefit'
                        },
                        {
                            'color': 'default',
                            'description': None,
                            'id': '7e8f879b-4b07-4387-80f5-b516576aa47c',
                            'name': 'Unknown'
                        }
                    ]
                },
                'type': 'select'
            },
            'Anaerobic': {
                'id': 'U%5C%3Eb',
                'name': 'Anaerobic',
                'number': {
                    'format': 'number'
                },
                'type': 'number'
            },
            'Anaerobic Effect': {
                'id': 'uKyX',
                'name': 'Anaerobic Effect',
                'select': {
                    'options': [
                        {
                            'color': 'red',
                            'description': None,
                            'id': 'rVCX',
                            'name': 'Overreaching'
                        },
                        {
                            'color': 'green',
                            'description': None,
                            'id': 'FJpb',
                            'name': 'Highly Impacting'
                        },
                        {
                            'color': 'blue',
                            'description': None,
                            'id': 'PfdA',
                            'name': 'Impacting'
                        },
                        {
                            'color': 'orange',
                            'description': None,
                            'id': '@mJg',
                            'name': 'Maintaining'
                        },
                        {
                            'color': 'yellow',
                            'description': None,
                            'id': 'qgQC',
                            'name': 'Some Benefit'
                        },
                        {
                            'color': 'gray',
                            'description': None,
                            'id': 'JPja',
                            'name': 'No Benefit'
                        },
                        {
                            'color': 'default',
                            'description': None,
                            'id': '1d2228bd-7356-4dd2-952d-ebdf82642707',
                            'name': 'Unknown'
                        }
                    ]
                },
                'type': 'select'
            },
            'Avg Pace': {
                'id': 'Bb%5DL',
                'name': 'Avg Pace',
                'rich_text': {},
                'type': 'rich_text'
            },
            'Calories': {
                'id': 'Mw%40U',
                'name': 'Calories',
                'number': {
                    'format': 'number'
                },
                'type': 'number'
            },
            'Created time': {
                'created_time': {},
                'id': '%3DW_B',
                'name': 'Created time',
                'type': 'created_time'
            },
            'Date': {
                'date': {},
                'id': '%5DKbq',
                'name': 'Date',
                'type': 'date'},
            'Distance (km)': {
                'id': 'u_%7B%3E',
                'name': 'Distance (km)',
                'number': {
                    'format': 'number'
                },
                'type': 'number'
            },
            'Duration (min)': {
                'id': 'W%3CN~',
                'name': 'Duration (min)',
                'number': {
                    'format': 'number'
                },
                'type': 'number'
            },
            'PR': {
                'checkbox': {},
                'id': 'Yg%7Bs',
                'name': 'PR',
                'type': 'checkbox'
            },
            'Subactivity Type': {
                'id': 'L%5B%3E%7D',
                'name': 'Subactivity Type',
                'select': {
                    'options': [
                        {
                            'color': 'green',
                            'description': None,
                            'id': ']iw?',
                            'name': 'Casual Walking'
                        },
                        {
                            'color': 'purple',
                            'description': None,
                            'id': '@hMi',
                            'name': 'Speed Walking'
                        },
                        {
                            'color': 'gray',
                            'description': None,
                            'id': '~|Vh',
                            'name': 'Indoor Rowing'
                        },
                        {
                            'color': 'yellow',
                            'description': None,
                            'id': 'ZBzK',
                            'name': 'Pilates'
                        },
                        {
                            'color': 'red',
                            'description': None,
                            'id': 'TpNx',
                            'name': 'Stair Stepper'
                        },
                        {
                            'color': 'default',
                            'description': None,
                            'id': 'aJNc',
                            'name': 'Yoga'
                        },
                        {
                            'color': 'blue',
                            'description': None,
                            'id': 'OHVa',
                            'name': 'Indoor Running'
                        },
                        {
                            'color': 'blue',
                            'description': None,
                            'id': 'KbLm',
                            'name': 'Street Running'
                        },
                        {
                            'color': 'blue',
                            'description': None,
                            'id': 'YneD',
                            'name': 'Treadmill Running'
                        },
                        {
                            'color': 'pink',
                            'description': None,
                            'id': '80d217c0-fe6f-4a14-9aa1-2b57eeb6c8bd',
                            'name': 'Indoor Cycling'},
                        {
                            'color': 'orange',
                            'description': None,
                            'id': 'f57d1dbc-1295-4430-acd7-09b0d6f4e0c8',
                            'name': 'Stretching'},
                        {
                            'color': 'brown',
                            'description': None,
                            'id': '7d11e53f-bd36-4371-ab38-9e1e477f6b38',
                            'name': 'Walking'},
                        {
                            'color': 'yellow',
                            'description': None,
                            'id': '1a6a046a-b0fa-4ff1-89ee-3b23a4303c39',
                            'name': 'Strength Training'},
                        {
                            'color': 'gray',
                            'description': None,
                            'id': '88bcf8c0-5e99-436e-a650-eb200d0dde2f',
                            'name': 'Hiking'},
                        {
                            'color': 'purple',
                            'description': None,
                            'id': 'fc250e79-ae89-4144-bd17-ea9b5fd895ef',
                            'name': 'Running'},
                        {
                            'color': 'gray',
                            'description': None,
                            'id': '49749ad6-dab6-4dd6-b4f6-326eefb634b5',
                            'name': 'Meditation'},
                        {
                            'color': 'red',
                            'description': None,
                            'id': '46aa3ed8-2960-461a-ab12-f8348c0ebf3d',
                            'name': 'Cycling'},
                        {
                            'color': 'gray',
                            'description': None,
                            'id': '8d76e5c8-22ab-413d-894e-05653d203111',
                            'name': 'Other'},
                        {
                            'color': 'gray',
                            'description': None,
                            'id': '7b514c30-7dcd-4eb9-90a9-997b4c88dd9b',
                            'name': 'Indoor Cardio'},
                        {
                            'color': 'orange',
                            'description': None,
                            'id': '890d5701-0491-446d-96bc-890360cd9cee',
                            'name': 'Strength'},
                        {
                            'color': 'purple',
                            'description': None,
                            'id': 'a7e1aade-f355-4104-8851-f9fa472d7cec',
                            'name': 'Barre'},
                        {
                            'color': 'default',
                            'description': None,
                            'id': 'e3207c52-095e-4214-b413-2610f7af9f4b',
                            'name': 'Rowing'},
                        {
                            'color': 'pink',
                            'description': None,
                            'id': '3747116d-069e-4ca6-8ae2-16837466b2a6',
                            'name': 'Breathwork'
                        }
                    ]
                },
                'type': 'select'
            },
            'Training Effect': {
                'id': 'TMOT',
                'name': 'Training Effect',
                'select': {
                    'options': [
                        {
                            'color': 'purple',
                            'description': None,
                            'id': 'I@Zy',
                            'name': 'Sprint'
                        },
                        {
                            'color': 'purple',
                            'description': None,
                            'id': 'dd79ae67-5429-4840-9e9c-d3dd23f1d847',
                            'name': 'Anaerobic Capacity'
                        },
                        {
                            'color': 'orange',
                            'description': None,
                            'id': '2c93e62a-59ba-4856-a10c-4e9d6114f1f2',
                            'name': 'Vo2Max'
                        },
                        {
                            'color': 'orange',
                            'description': None,
                            'id': 'a764cbe3-b533-4f2b-a6fc-7e83a5d7d7de',
                            'name': 'Lactate Threshold'
                        },
                        {
                            'color': 'orange',
                            'description': None,
                            'id': 'f36f17bb-fe6a-4d50-9cdd-4dde614e7401',
                            'name': 'Tempo'
                        },
                        {
                            'color': 'green',
                            'description': None,
                            'id': 'e50bf6bc-0678-4721-813c-9307bb710d59',
                            'name': 'Aerobic Base'
                        },
                        {
                            'color': 'green',
                            'description': None,
                            'id': 'b1bc6838-1e7d-4119-b47d-aa370de047ae',
                            'name': 'Recovery'
                        },
                        {
                            'color': 'default',
                            'description': None,
                            'id': 'b2eb2752-50f1-4e79-bcf4-dd35b988f145',
                            'name': 'Unknown'
                        }
                    ]
                },
                'type': 'select'
            }
        },
        'public_url': None,
        'request_id': 'e9d18d4c-943c-41f9-9f4a-f9948ba54b2c',
        'title': [
            {
                'annotations': {
                    'bold': False,
                    'code': False,
                    'color': 'default',
                    'italic': False,
                    'strikethrough': False,
                    'underline': False
                },
                'href': None,
                'plain_text': 'Activities',
                'text': {
                    'content': 'Activities',
                    'link': None
                },
                'type': 'text'
            }
        ],
        'url': 'https://www.notion.so/381d8720f394468ea63d9f75aec3064d'
    }
