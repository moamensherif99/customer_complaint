{
    'name': 'Customer Complaint',
    'author': 'Moamen Sherif Abdelkader',
    'category': '',
    'version': '17.0.1.0',
    'depends': ['base','sale_management','account','mail','hr'
                ],
    'data': [
        "security/ir.model.access.csv",
        "data/sequence.xml",
        "views/customer_complaint_view.xml",
        "views/base_menu.xml",
    ],
    'assets': {

    },
    'application': True,
}
