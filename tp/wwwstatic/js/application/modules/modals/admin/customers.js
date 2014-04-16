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
                    'change input[name=groupSelect]'        :   'toggle',
                    'change input[name=userSelect]'         :   'toggle',
                    'click button[name=cancelEditCustomer]' :   'toggleAclAccordion',
                    'click #submitCustomer'                 :   'verifyForm',
                    'click button[name=submitEditCustomer]' :   'verifyForm',
                    'change #customerContext'               :   'changeCustomerContext'
                },
                changeCustomerContext: function (event) {
                    this.collection.params.customer_name = this.customerContext = event.val;
                    this.collection.fetch();
                    return this;
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
                    return this;
                },
                toggle: function (event) {
                    var $input = $(event.currentTarget),
                        customername = $input.data('customer'),
                        groupId = $input.data('id'),
                        url = $input.data('url') + '/' + customername,
                        $alert = this.$el.find('div.alert'),
                        params,
                        customers = [],
                        groups = [];
                    customers.push(customername);
                    groups.push(groupId);
                    params = {
                        customer_names: customers,//event.added ? event.added.text : event.removed.text,
                        action: event.added ? 'add' : 'delete'
                    };
                    console.log(customername);
                    $.ajax({
                        type: 'POST',
                        url: url,
                        data: JSON.stringify(params),
                        dataType: 'json',
                        contentType: 'application/json',
                        success: function(response) {
                            if (response.rv_status_code) {
                                $alert.hide();
                            } else {
                                $alert.removeClass('alert-success').addClass('alert-error').show().find('span').html(response.message);
                            }
                        }
                    }).error(function (e) { window.console.log(e.responseText); });
                    return this;
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
                    return this;
                },
                beforeRender: $.noop,
                onRender: function () {
                    var $users = this.$('select[name=users]'),
//                        $customers = this.$('select[name=customers]'),
                        $select = this.$el.find('input[name=groupSelect], input[name=userSelect]'),
                        that = this;
                    $users.select2({width: '100%'});
//                    $customers.select2({width: '100%'});
                    $select.select2({
                        width: '100%',
                        multiple: true,
                        initSelection: function (element, callback) {
                            var data = JSON.parse(element.val()),
                                results = [];

                            _.each(data, function (object) {
                                results.push({id: object.id || object.user_name, text: object.group_name ? object.group_name : object.user_name});
                            });
                            callback(results);
                        },
                        ajax: {
                            url: function () {
                                return $(that).data('url');
                            },
                            data: function () {
                                return {
                                    customer_name: that.customerContext
                                };
                            },
                            results: function (data) {
                                var results = [];
                                if (data.rv_status_code === 1001) {
                                    _.each(data.data, function (object) {
                                        results.push({id: object.id || object.user_name, text: object.group_name ? object.group_name : object.user_name});
                                    });
                                    return {results: results, more: false, context: results};
                                }
                            }
                        }
                    });
                    return this;
                },
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
                            loggedInUser: customers.user_name,
                            viewHelpers: {
                                getOptions: function (options, selected) {
                                    var select = crel('select'), attributes;
                                    selected = selected || false;
                                    if (options.length) {
                                        _.each(options, function (option) {
                                            if (_.isUndefined(option.administrator) || option.administrator) {
//                                                if(option.user_name)
//                                                {
                                                    attributes = {value: option.user_name};
                                                    if (selected && option.user_name === selected) {attributes.selected = selected;}
                                                    select.appendChild(crel('option', attributes, option.user_name));
//                                                }
                                            }
                                        });
                                    }
                                    return select.innerHTML;
                                },
                                renderDeleteButton: function (customer) {
                                    var fragment;
//                                    if (customer.customer_name !== 'default') {
                                        fragment = crel('div');
                                        fragment.appendChild(
                                            crel('button', {class: 'btn btn-link noPadding', name: 'toggleDelete'},
                                                crel('i', {class: 'icon-remove', style: 'color: red'}))
                                        );
                                        return fragment.innerHTML;
//                                    }
                                },
                                renderCustomerLink: function (customer) {
                                    var fragment = crel('div');
                                    fragment.appendChild(
                                        crel('button', {name: 'toggleAcl', class: 'btn btn-link noPadding'},
                                            crel('i', {class: 'icon-circle-arrow-down'}, ' '),
                                            crel('span', customer.customer_name)
                                        )
                                    );
                                   /* if (customer.customer_name !== 'default') {
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
                                    }*/
                                    return fragment.innerHTML;
                                }
                            }
                        };
                        this.$el.empty();
                        this.$el.html(template(payload));
                        console.log(payload);
                        if (this.onRender !== $.noop) { this.onRender(); }
                    }
                    return this;
                }
            })
        };
        return exports;
    }
);
