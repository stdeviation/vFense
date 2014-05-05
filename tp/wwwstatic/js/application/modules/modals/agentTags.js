define(
    ['jquery', 'underscore', 'backbone', 'crel', 'modals/panel', 'select2'],
    function ($, _, Backbone, crel, Panel) {
        'use strict';
        var viewOptions = ['id', 'agentName', 'tags', 'type'], exports = {};
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
                    this.setContentHTML(this.renderAgentTags());

                    if (this.onRenderAgentTags !== $.noop)
                     {
                        this.onRenderAgentTags();
                     }
                    return this;
                },
                events: function () {
                    return _.extend({
                        'click .close': 'close'
                    }, _.result(Panel.View.prototype, 'events'));
                },
                renderAgentTags: function () {
                    return crel('div',
                               crel('label', {for: 'agentTagSelect2'}, 'Tags for Agent ',
                                   crel('strong', this.agentName), ':'
                               ),
                               crel('input', {type: 'hidden', id: 'agentTagSelect2', name: 'agentTagSelect2', value: JSON.stringify(this.tags)})
                    );
                },
                onRenderAgentTags: function () {
                    var $agentTagSelect2 = this.$el.find('#agentTagSelect2'),
                        that = this;

                    $agentTagSelect2.on('select2-opening', function(event){
                        event.preventDefault();
                    });

                    $agentTagSelect2.select2({
                        width: '100%',
                        multiple: true,
                        initSelection: function (element, callback) {
                            var data = JSON.parse(element.val()),
                                results = [];

                            _.each(data, function (object) {
                                results.push({locked: true, id: object.tag_id, text: object.tag_name});
                            });
                            callback(results);
                        },
                        ajax: {
                            url: function () {
                                return $agentTagSelect2.data('url');
                            },
                            data: {

                            },
                            results: function (data) {
                                var results = [];
                                if (data.rv_status_code === 1001) {
                                    _.each(data.data, function (object) {
                                        results.push({id: object.tag_id, text: object.tag_name});
                                    });
                                    return {results: results, more: false, context: results};
                                }
                            }
                        }
                    });
                    return this;
                }
            })
        });
        return exports;
    }
);