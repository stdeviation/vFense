define(
    ['jquery', 'underscore', 'backbone', 'crel', 'modals/panel'],
    function ($, _, Backbone, crel, Panel) {
        'use strict';
        var viewOptions = ['id', 'url', 'name', 'type', 'redirect', 'data', 'customers'], exports = {};
        _.extend(exports, {
            View: Panel.View.extend({
                id: '',
                type: '',
                data: {},
                initialize: function (options) {
                    if (_.isObject(options)) {
                        _.extend(this, _.pick(options, viewOptions));
                    }
                    Panel.View.prototype.initialize.call(this);
                    this.setHeaderHTML(this.renderDeleteHeader())
                        .setContentHTML(this.renderDeleteContent());
                },
                events: function () {
                    return _.extend({
                        'click .close': 'close'
                    }, _.result(Panel.View.prototype, 'events'));
                },
                renderDeleteHeader: function () {
                    return crel('div', {class: 'row-fluid'},
                        crel('h4', {class: 'pull-left'}, 'Are you ABSOLUTELY sure?'),
                        crel('button', {type: 'button', class: 'close pull-right noMargin', 'aria-hidden': 'true'},
                            crel('i', {class: 'icon-remove'})
                        )
                    );
                },
                renderDeleteContent: function () {
                    return crel('div', {class: 'customerRemovalDiv'},
                               crel('label', {for: 'deleteAllAgents'}, 'Type yes to Delete All the Agents'),
                               crel('input', {type: 'text', id: 'deleteAllAgents', required: 'required'}),
                               crel('label', {for: 'moveAgents'}, 'Select a Customer to Move All the Agents to it'),
                               crel('select', {id: 'moveAgents'}, this.getCustomers())
                           );
                },
                getCustomers: function() {
                    var optionFragment = document.createDocumentFragment(),
                        that = this;
                    _.each(this.customers, function(customer) {
                        if(customer.customer_name !== that.name)
                        {
                            optionFragment.appendChild(crel('option', {value: customer.customer_name}, customer.customer_name));
                        }
                    });
                    return optionFragment;
                },
                confirm: function () {
                    var $button = this.$('button.btn-danger'),
                        $message = this.$('div.help-online'),
                        that = this,
                        params = {
                            delete_all_agents: that.$el.find('#deleteAllAgents').val(),
                            move_agents_to_customer: that.$el.find('#moveAgents').val()
                        };

                        $.ajax({
                            url: that.url + '/' + that.name,
                            data: JSON.stringify(params),
                            type: 'DELETE',
                            contentType: 'application/json',
                            success: function (response) {
                                if (response.http_status === 200) {
                                    console.log('successful');
                                    /*that.cancel();
                                    if (that.redirect === document.location.hash) {
                                        document.location.reload();
                                    } else if (that.redirect) {
                                        document.location.hash = that.redirect;
                                    }*/
                                } else {
                                    $message.addClass('alert-error').html(response.message);
                                }
                            },
                            error: function (response) {
                                $message.addClass('alert-error').html(response.responseJSON.message);
                            }
                        });
                    return this;
                },
                /*toggleDeleteDisable: function (event) {
                    var $input = $(event.currentTarget),
                        $button = this.$('button.btn-danger'),
                        value = $input.val();
                    if (value === 'DELETE') {
                        $button.removeClass('disabled');
                    } else {
                        if (!$button.hasClass('disabled')) {
                            $button.addClass('disabled');
                        }
                    }
                },*/
                span: '6',
                buttons: [
                    {
                        text: 'I understand and would like to delete this customer',
                        action: 'confirm',
                        style: 'width: 100%',
                        className: 'btn-danger'
                    }
                ]
            })
        });
        return exports;
    }
);