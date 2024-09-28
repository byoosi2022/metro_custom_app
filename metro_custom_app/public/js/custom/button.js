frappe.ui.form.on('Leasing', {
    refresh: function(frm) {
        if (frm.doc.docstatus === 1 && !frm.doc.__is_payment_created) {
            frm.add_custom_button(__('pay'), function() {
                frappe.call({
                    method: 'metro_custom_app.custom_api.pay.make_payment_for_invoice',
                    args: {
                        invoice_id: frm.doc.invoice,
                        amount: frm.doc.amount_approved,
                    
                    },
                    callback: function(response) {
                        console.log(frm.doc.name);
                        if (response.message) {
                            var pe_id = response.message;
                            frm.doc.__is_payment_created = true; // Set flag to indicate payment created
                            
                            // Create Payment Entry with custom_requisition_id set to Leasing document name
                            frappe.model.with_doctype('Payment Entry', function() {
                                var pe = frappe.model.get_new_doc('Payment Entry');
                                pe.custom_requisition_id = frm.doc.name;
                                frappe.set_route('Form', 'Payment Entry', pe_id); // Open Payment Entry form
                            });
                        } else {
                            frappe.msgprint('Failed to create Payment Entry');
                        }
                    }
                });
            }, __("Create Payment"));
        }
    }
});

frappe.ui.form.on('Purchase Receipt', {
    refresh: function(frm) {
        if (frm.doc.docstatus === 1) {
        frm.add_custom_button(
            __("Post Receipt to Server 1"),
            function () {
                frappe.call({
                    method: 'metro_custom_app.post_offline_1.purchase_reciept.post_purchase_receipts',
                    args:{
                        docname: frm.doc.name
                    },
                    callback: function(response) {
                        console.log(response)
                        frappe.msgprint(response.message);
                    }
                });
                
            },
            __("Post")
        );

        frm.add_custom_button(
            __("Post Receipt to Server 2"),
            function () {
                frappe.call({
                    method: 'metro_custom_app.post_offline.purchase_reciept.post_purchase_receipts',
                    args:{
                        docname: frm.doc.name
                    },
                    callback: function(response) {
                        console.log(response)
                        frappe.msgprint(response.message);
                    }
                });
                
            },
            __("Post")
        );
        frm.add_custom_button(
            __("Post Receipt to Server 3"),
            function () {
                frappe.call({
                    method: 'metro_custom_app.post_offline_3.purchase_reciept.post_purchase_receipts',
                    args:{
                        docname: frm.doc.name
                    },
                    callback: function(response) {
                        console.log(response)
                        frappe.msgprint(response.message);
                    }
                });
                
            },
            __("Post")
        );
    }
    }
});


frappe.ui.form.on('Stock Reconciliation', {
    refresh: function(frm) {
        if (frm.doc.docstatus === 1) {
        frm.add_custom_button(
            __("Post Reconciliation to Server 1"),
            function () {
                frappe.call({
                    method: 'metro_custom_app.post_offline_1.stock_reconsilation.post_stock_reconciliation',
                    args:{
                        docname: frm.doc.name
                    },
                    callback: function(response) {
                        frappe.msgprint(response.message);
                    }
                });
                
            },
            __("Post")
        );
        frm.add_custom_button(
            __("Post Reconciliation to Server 2"),
            function () {
                frappe.call({
                    method: 'metro_custom_app.post_offline.stock_reconsilation.post_stock_reconciliation',
                    args:{
                        docname: frm.doc.name
                    },
                    callback: function(response) {
                        frappe.msgprint(response.message);
                    }
                });
                
            },
            __("Post")
        );
        frm.add_custom_button(
            __("Post Reconciliation to Server 3"),
            function () {
                frappe.call({
                    method: 'metro_custom_app.post_offline_3.stock_reconsilation.post_stock_reconciliation',
                    args:{
                        docname: frm.doc.name
                    },
                    callback: function(response) {
                        frappe.msgprint(response.message);
                    }
                });
                
            },
            __("Post")
        );
    }
    }
});

frappe.ui.form.on('Stock Entry', {
    refresh: function(frm) {

    if (frm.doc.docstatus === 1) {
        frm.add_custom_button(
            __("Post Stock Transfer to Server 1"),
            function () {
                frappe.call({
                    method: 'metro_custom_app.post_offline_1.stock_entry.post_stock_entry',
                    args:{
                        docname: frm.doc.name
                    },
                    callback: function(response) {
                        frappe.msgprint(response.message);
                    }
                });
                
            },
            __("Post")
        );

        frm.add_custom_button(
            __("Post Stock Transfer to Server 2"),
            function () {
                frappe.call({
                    method: 'metro_custom_app.post_offline.stock_entry.post_stock_entry',
                    args:{
                        docname: frm.doc.name
                    },
                    callback: function(response) {
                        frappe.msgprint(response.message);
                    }
                });
                
            },
            __("Post")
        );

        frm.add_custom_button(
            __("Post Stock Transfer to Server 3"),
            function () {
                frappe.call({
                    method: 'metro_custom_app.post_offline_3.stock_entry.post_stock_entry',
                    args:{
                        docname: frm.doc.name
                    },
                    callback: function(response) {
                        frappe.msgprint(response.message);
                    }
                });
                
            },
            __("Post")
        );
    }
    
    }
});

frappe.ui.form.on('Item', {
    refresh: function(frm) {

        frm.add_custom_button(
            __("Post Item to Server 1"),
            function () {
                frappe.call({
                    method: 'metro_custom_app.post_offline_1.item_creation.create_item',
                    args:{
                        docname: frm.doc.name
                    },
                    callback: function(response) {
                        frappe.msgprint(response.message);
                    }
                });
                
            },
            __("Post")
        );
        frm.add_custom_button(
            __("Post Item to Server 2"),
            function () {
                frappe.call({
                    method: 'metro_custom_app.post_offline.item_creation.create_item',
                    args:{
                        docname: frm.doc.name
                    },
                    callback: function(response) {
                        frappe.msgprint(response.message);
                    }
                });
                
            },
            __("Post")
        );
        frm.add_custom_button(
            __("Post Item to Server 3"),
            function () {
                frappe.call({
                    method: 'metro_custom_app.post_offline_3.item_creation.create_item',
                    args:{
                        docname: frm.doc.name
                    },
                    callback: function(response) {
                        frappe.msgprint(response.message);
                    }
                });
                
            },
            __("Post")
        );

    }
});

frappe.ui.form.on('Purchase Order', {
    refresh: function(frm) {
        if (frm.doc.docstatus === 1) {
            
            frm.add_custom_button(
                __("Update Item Prices server 1"),
                function () {
                    frappe.call({
                        method: 'metro_custom_app.post_offline_1.item_price_order.post_item_price',
                        args:{
                            docname: frm.doc.name
                        },
                        callback: function(response) {
                            frappe.msgprint(response.message);
                        }
                    });
                },
                __("Post")
            );

            frm.add_custom_button(
                __("Update Item Prices server 2"),
                function () {
                    frappe.call({
                        method: 'metro_custom_app.post_offline.item_price_order.post_item_price',
                        args:{
                            docname: frm.doc.name
                        },
                        callback: function(response) {
                            frappe.msgprint(response.message);
                        }
                    });
                },
                __("Post")
            );

            frm.add_custom_button(
                __("Update Item Prices server 3"),
                function () {
                    frappe.call({
                        method: 'metro_custom_app.post_offline_3.item_price_order.post_item_price',
                        args:{
                            docname: frm.doc.name
                        },
                        callback: function(response) {
                            frappe.msgprint(response.message);
                        }
                    });
                },
                __("Post")
            );


        }
    }
});


frappe.ui.form.on('Supplier', {
    refresh: function(frm) {
                   
            frm.add_custom_button(
                __("Update Supplier server 1"),
                function () {
                    frappe.call({
                        method: 'metro_custom_app.post_offline_1.supplier.create_or_update_supplier',
                        args:{
                            docname: frm.doc.name
                        },
                        callback: function(response) {
                            frappe.msgprint(response.message);
                        }
                    });
                },
                __("Post")
            );

            frm.add_custom_button(
                __("Update Supplier server 2"),
                function () {
                    frappe.call({
                        method: 'metro_custom_app.post_offline.supplier.create_or_update_supplier',
                        args:{
                            docname: frm.doc.name
                        },
                        callback: function(response) {
                            frappe.msgprint(response.message);
                        }
                    });
                },
                __("Post")
            );

            frm.add_custom_button(
                __("Update Supplier server 3"),
                function () {
                    frappe.call({
                        method: 'metro_custom_app.post_offline_3.supplier.create_or_update_supplier',
                        args:{
                            docname: frm.doc.name
                        },
                        callback: function(response) {
                            frappe.msgprint(response.message);
                        }
                    });
                },
                __("Post")
            );


        
    }
});

frappe.ui.form.on('Customer', {
    refresh: function(frm) {
                   
            frm.add_custom_button(
                __("Update Customer server 1"),
                function () {
                    frappe.call({
                        method: 'metro_custom_app.post_offline_1.customer.create_or_update_customer',
                        args:{
                            docname: frm.doc.name
                        },
                        callback: function(response) {
                            frappe.msgprint(response.message);
                        }
                    });
                },
                __("Post")
            );

            frm.add_custom_button(
                __("Update Customer server 2"),
                function () {
                    frappe.call({
                        method: 'metro_custom_app.post_offline.customer.create_or_update_customer',
                        args:{
                            docname: frm.doc.name
                        },
                        callback: function(response) {
                            frappe.msgprint(response.message);
                        }
                    });
                },
                __("Post")
            );

            frm.add_custom_button(
                __("Update Customer server 3"),
                function () {
                     frappe.call({
                        method: 'metro_custom_app.post_offline_3.customer.create_or_update_customer',
                        args:{
                            docname: frm.doc.name
                        },
                        callback: function(response) {
                            console.log("response")
                            frappe.msgprint(response.message);
                        }
                    });
                },
                __("Post")
            );


        
    }
});

frappe.ui.form.on('Item Price', {
    refresh: function(frm) {
                   
            frm.add_custom_button(
                __("Update Item Price server 1"),
                function () {
                    frappe.call({
                        method: 'metro_custom_app.post_offline_1.item_price.create_or_update_item_price',
                        args:{
                            docname: frm.doc.name
                        },
                        callback: function(response) {
                            frappe.msgprint(response.message);
                        }
                    });
                },
                __("Post")
            );

            frm.add_custom_button(
                __("Update Item Price server 2"),
                function () {
                    frappe.call({
                        method: 'metro_custom_app.post_offline.item_price.post_item_price',
                        args:{
                            docname: frm.doc.name
                        },
                        callback: function(response) {
                            frappe.msgprint(response.message);
                        }
                    });
                },
                __("Post")
            );

            frm.add_custom_button(
                __("Update Item Price server 3"),
                function () {
                    frappe.call({
                        method: 'metro_custom_app.post_offline_3.item_price.create_or_update_item_price',
                        args:{
                            docname: frm.doc.name
                        },
                        callback: function(response) {
                            frappe.msgprint(response.message);
                        }
                    });
                },
                __("Post")
            );


    }
});

frappe.ui.form.on('User', {
    refresh: function(frm) {
                   
            frm.add_custom_button(
                __("Update User server 1"),
                function () {
                    frappe.call({
                        method: 'metro_custom_app.post_offline_1.user.post_users',
                        args:{
                            docname: frm.doc.name
                        },
                        callback: function(response) {
                            frappe.msgprint(response.message);
                        }
                    });
                },
                __("Post")
            );

            frm.add_custom_button(
                __("Update User server 2"),
                function () {
                    frappe.call({
                        method: 'metro_custom_app.post_offline.user.post_users',
                        args:{
                            docname: frm.doc.name
                        },
                        callback: function(response) {
                            frappe.msgprint(response.message);
                        }
                    });
                },
                __("Post")
            );
            frm.add_custom_button(
                __("Update User server 3"),
                function () {
                    frappe.call({
                        method: 'metro_custom_app.post_offline_3.user.post_users',
                        args:{
                            docname: frm.doc.name
                        },
                        callback: function(response) {
                            frappe.msgprint(response.message);
                        }
                    });
                },
                __("Post")
            );



        
    }
});

frappe.ui.form.on('Lead', {
    refresh: function(frm) {
                   
            frm.add_custom_button(
                __("Update User server 1"),
                function () {
                    frappe.call({
                        method: 'metro_custom_app.post_offline_1.Lead.create_lead',
                        // args:{
                        //     docname: frm.doc.name
                        // },
                        callback: function(response) {
                            frappe.msgprint(response.message);
                        }
                    });
                },
                __("Post")
            );


        
    }
});


// frappe.ui.form.on('Payment Request', {
//     onload: function(frm) {
//         // Check if custom_status field is not set
//         if (!frm.doc.custom_status) {
//             frappe.call({
//                 method: 'metro_custom_app.custom_api.update_status.update_custom_status',
//                 args: {
//                     payment_request_name: frm.doc.name
//                 },
//                 callback: function(response) {
//                     if (response.message.status === 'success') {
//                         frm.reload_doc(); // Reload the document to reflect the changes
//                     } else {
//                         frappe.msgprint(__('Error: ' + response.message.message));
//                     }
//                 }
//             });
//         }
//     }
// });









