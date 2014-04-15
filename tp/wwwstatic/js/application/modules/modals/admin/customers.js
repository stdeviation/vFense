define(
    ['jquery', 'underscore', 'backbone', 'app', 'crel', 'modals/admin/deleteCustomer', 'text!templates/modals/admin/customers.html'],
    function ($, _, Backbone, app, crel, DeleteCustomerModal, CustomersTemplate) {
        'use strict';var exports = {
            Collection: Backbone.Collection.extend({
                baseUrl: 'api/v1/customers',
                params: {},
                url: function () {
                    return this.baseUrl + '?' + $.param(this.params);
                }
                /*url: function () {
                    return this.baseUrl;
                },
                parse: function (response) {
                    return response.rv_status_code === 1001 ? response.data : [];
                }*/
            }),
            UserCollection: Backbone.Collection.extend({
                baseUrl: 'api/v1/users',
                url: function () {
                    return this.baseUrl;
                }
            }),
            View: Backbone.View.extend({
                initialize: function () {
                    var that = this;
                    this.template = _.template(CustomersTemplate);
                    this.collection = new exports.Collection();
                    this.listenTo(this.collection, 'sync', this.render);
                    this.collection.fetch();
                    this.userCollection = new exports.UserCollection();
                    this.listenTo(this.userCollection, 'sync', this.render);
                    this.userCollection.fetch();
                    return this;
                },
                events: {
                    'click button[name=toggleAcl]'          :   'toggleAclAccordion',
                    'click button[name=toggleDelete]'       :   'confirmDelete',
                    'click button[name=deleteCustomer]'     :   'deleteCustomer',
                    'click button[data-id=toggleCustomer]'  :   'createCustomer',
                    'click #cancelNewCustomer'              :   'createCustomer',
                    'click button[name=cancelEditCustomer]' :   'toggleAclAccordion',
                    'click #submitCustomer'                 :   'verifyForm',
                    'click button[name=submitEditCustomer]' :   'verifyForm'
                },
                toggleAclAccordion: function (event) {
                    event.preventDefault();
                    var $icon,
                        $href = $(event.currentTarget),
                        $accordionParent = $href.parents('.accordion-group'),
                        $accordionBody = $accordionParent.find('.accordion-body').first();
//                        editCustomerForm = this.$('#newCustomerDiv');
                    if($href.attr('name') === 'toggleAcl')
                    {
                        $icon = $href.find('i');
                        $icon.toggleClass('icon-circle-arrow-down icon-circle-arrow-up');
                    }
                    else if($href.attr('name') === 'cancelEditCustomer')
                    {
                        $icon = $href.parents('.accordion-group').find('.accordion-heading').find('i');
                        $icon.toggleClass('icon-circle-arrow-down icon-circle-arrow-up');
                    }

//                    editCustomerForm.removeClass('hide');
//                    $accordionBody.html(editCustomerForm);
//                    editCustomerForm.toggle();
                    $accordionBody.unbind().collapse('toggle');
                    $accordionBody.on('hidden', function (event) {
                        event.stopPropagation();
                    });
                    return this;
                },
                confirmDelete: function (event) {
                    var $parentDiv = $(event.currentTarget).parent();
                    $parentDiv.children().toggle();
                    return this;
                },
                deleteCustomer: function (event) {
                    var that = this,
                        DeletePanel = DeleteCustomerModal.View.extend({
//                            confirm: that.deleteCustomer
                        });
                    if (this.deleteCustomerModal) {
                        this.deleteCustomerModal.close();
                        this.deleteCustomerModal = undefined;
                    }

                    this.deleteCustomerModal = new DeletePanel({
                        name: $(event.currentTarget).val(),
                        type: 'customer',
                        url: 'api/v1/customer',
                        customers: app.user.toJSON().customers
                    }).open();
                    /*var $deleteButton = $(event.currentTarget),
                        $customerRow = $deleteButton.parents('.item'),
                        $alert = this.$el.find('div.alert'),
                        customer = $deleteButton.val();
                    console.log(customer);
                    *//* params = {
                     username: user
                     };*//*
                    $.ajax({
                        type: 'DELETE',
                        url: '/api/v1/customer/' + customer,
                        dataType: 'json',
                        contentType: 'application/json',
                        success: function(response){
                            if (response.rv_status_code) {
                                $customerRow.remove();
                                $alert.removeClass('alert-error').addClass('alert-success').show().find('span').html(response.message);
                            } else {
                                $alert.removeClass('alert-success').addClass('alert-error').show().find('span').html(response.message);
                            }
                        }
                    });*/
                    return this;
                },
                createCustomer: function (event) {
                    event.preventDefault();
                    var $newCustomerDiv = this.$('#newCustomerDiv');
                    $newCustomerDiv.toggle();
                    return this;
                },
                verifyForm: function (event) {
                    var form = document.getElementById('newCustomerDiv');
                    if (form.checkValidity()) {
                        this.submitCustomer(event);
                    }
                },
                submitCustomer: function (event) {
                    event.preventDefault();
                    var customerName = this.$el.find('#customerName').val(),
                        downloadURL = this.$el.find('#downloadURL').val(),
                        netThrottle = this.$el.find('#netThrottle').val(),
                        cpuThrottle = this.$el.find('#cpuThrottle').val(),
                        serverQueueTTL = this.$el.find('#serverQueueTTL').val(),
                        agentQueueTTL = this.$el.find('#agentQueueTTL').val(),
                        $alert = this.$('#newCustomerDiv').find('.help-online'),
                        url = 'api/v1/customers',
                        that = this,
                        params = {
                            customer_name: customerName,
                            download_url: downloadURL,
                            net_throttle: netThrottle,
                            cpu_throttle: cpuThrottle,
                            server_queue_ttl: serverQueueTTL,
                            agent_queue_ttl: agentQueueTTL
                        };
                    $.ajax({
                        type: 'POST',
                        url: 'api/v1/customers',
                        data: JSON.stringify(params),
                        dataType: 'json',
                        contentType: 'application/json',
                        success: function(response) {
                            if (response.rv_status_code) {
                                that.collection.fetch();
                            } else {
                                $alert.removeClass('alert-success').addClass('alert-error').html(response.message).show();
                            }
                        }
                    });
                    /*$.post(url, params, function (json) {
                     if (json.rv_status_code) {
                     app.vent.trigger('customer:change', null);
                     that.collection.fetch();
                     } else {
                     app.notifyOSD.createNotification('!', 'Error', json.message);
                     }
                     });*/
                },
                beforeRender: $.noop,
                onRender: $.noop,
                render: function () {
                    if (this.beforeRender !== $.noop) { this.beforeRender(); }

                    var template = this.template,
                        data = this.collection.toJSON()[0],
                        users = this.userCollection.toJSON()[0],
                        customers = app.user.toJSON(),
                        payload;

                    if (data && data.rv_status_code === 1001 && users && users.rv_status_code === 1001) {
                        payload = {
                            data: data.data,
                            users: users.data,
                            customers: customers.customers,
                            viewHelpers: {
                                getOptions: function (options, selected) {
                                    var select = crel('select'), attributes;
                                    selected = selected || false;
                                    if (options.length) {
                                        _.each(options, function (option) {
                                            if (_.isUndefined(option.administrator) || option.administrator) {
                                                if(option.user_name)
                                                {
                                                    attributes = {value: option.user_name};
                                                    if (selected && option.user_name === selected) {attributes.selected = selected;}
                                                    select.appendChild(crel('option', attributes, option.user_name));
                                                }
                                            }
                                        });
                                    }
                                    return select.innerHTML;
                                },
                                renderDeleteButton: function (customer) {
                                    var fragment;
                                    if (customer.customer_name !== 'administrator') {
                                        fragment = crel('div');
                                        fragment.appendChild(
                                            crel('button', {class: 'btn btn-link noPadding', name: 'toggleDelete'},
                                                crel('i', {class: 'icon-remove', style: 'color: red'}))
                                        );
                                        return fragment.innerHTML;
                                    }
                                },
                                renderCustomerLink: function (customer) {
                                    var fragment = crel('div');
                                    if (customer.customer_name !== 'administrator') {
                                        fragment.appendChild(
                                            crel('button', {name: 'toggleAcl', class: 'btn btn-link noPadding'},
                                                crel('i', {class: 'icon-circle-arrow-down'}, ' '),
                                                crel('span', customer.customer_name)
                                            )
                                        );
                                    } else {
                                        fragment.appendChild(
                                            crel('strong', customer.customer_name)
                                        );
                                    }
                                    return fragment.innerHTML;
                                }
                            }
                        };
                        this.$el.empty();
                        this.$el.html(template(payload));
                        if (this.onRender !== $.noop) { this.onRender(); }
                    }


                   /* var $el = this.$el;
                    if ($el.children().length === 0) {
                        $el.html(this.layout());
                    }
                    this.renderHeader();
                    this.renderList();*/

                    return this;
                }
               /* layout: function () {
                    var fragment = document.createDocumentFragment();
                    fragment.appendChild(
                        crel('section', {class: 'list'},
                            crel('header', {class: 'row-fluid clearfix', id: 'header'}),
                            crel('header', {class: 'row-fluid clearfix hide', id: 'toggleDiv'}),
                            crel('div', {class: 'items'})
                        )
                    );
                    return fragment;
                },*/
                /*,
                deleteCustomer: function () {
                    var $button = this.$('button.btn-danger'),
                        customer = this.name,
                        url = '/api/v1/customers',
                        that = this,
                        params = {
                            name: customer
                        };
                    if (!$button.hasClass('disabled')) {
                        $.post(url, params, function (json) {
                            if (json.rv_status_code) {
                                app.vent.trigger('customer:change', null);
                                that.collection.fetch();
                            } else {
                                app.notifyOSD.createNotification('!', 'Error', json.message);
                            }
                        });
                    }
                },
                renderHeader: function () {
                    var $header = this.$('#header'),
                        $toggleDiv = this.$('#toggleDiv');
                    $header.empty();
                    $toggleDiv.empty();
                    $header.append(
                        crel('span', {class: 'pull-right'},
                            crel('button', {class: 'btn btn-mini', 'data-id': 'toggleCustomer'},
                                crel('i', {class : 'icon-plus', style: 'color: green'}),
                                crel('strong', ' Create Customer')
                            )
                        )
                    );
                    $toggleDiv.append(
                        crel('span',
                            crel('input', {type: 'text', placeholder: 'New Customer', id: 'customerInput'})
                        ),
                        crel('span', {class: 'pull-right'},
                            crel('button', {class: 'btn btn-mini btn-danger', 'data-id': 'toggleCustomer'}, 'Cancel'),  ' ',
                            crel('button', {class: 'btn btn-mini btn-primary', 'data-id': 'submitCustomer'}, 'Submit')
                        )
                    );
                },
                renderList: function () {
                    var $list = this.$('.items'),
                        data = this.collection.toJSON();
                    $list.empty();
                    if (data.length) {
                        _.each(data, function (item) {
                            $list.append(
                                crel('div', {class: 'item row-fluid'}, item.customer_name,
                                    crel('span', {class: 'pull-right'},
                                        crel('button', {class: 'btn btn-link noPadding', 'data-id': 'toggleDelete', 'data-customer_name': item.customer_name},
                                            crel('i', {class: 'icon-remove', style: 'color: red'})
                                        ),
                                        crel('button', {class: 'btn btn-mini btn-danger hide', 'data-id': 'deleteCustomer'}, 'Delete'), ' ',
                                        crel('button', {class: 'btn btn-mini hide', 'data-id': 'toggleDelete'}, 'Cancel')
                                    )
                                )
                            );
                        });
                    } else {
                        $list.append(
                            crel('div', {class: 'item row-fluid'}, 'No Customers Available')
                        );
                    }
                }*/
            })
        };
        return exports;
    }
);
