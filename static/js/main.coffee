class LayoutViewModel
    constructor: ->
        @header = ko.observable({})
        @layoutItems = ko.observableArray()

        @_requestLayout()

    addWidgetInfo: (index) ->
        return index
        console.log(index)

    addWidget: ->
        $('#add-widget-dialog').dialog({})
        console.log($('#add-widget-dialog'))
        #model.index
        #console.log(foo)
        #console.log(bar)

    addGallery: (index) ->
        console.log(index)

    _requestLayout: =>
        callback = (data) =>
            console.log(data)
            @header({ text: data.header })

            for widget in data.widgets            
                @layoutItems.push(widget)
            console.log(@layoutItems())
        $.getJSON("/layout", callback)


ready = ->
    ko.applyBindings(new LayoutViewModel())
    console.log('starting knockout')

$(document).ready(ready)
$(document).on('page:load', ready)
