$.contextMenu({
    selector: '.right-click-edit', 
    build: ($trigger, e) ->
        console.log($trigger[0])
        console.log($trigger)
        console.log(e)
        # this callback is executed every time the menu is to be shown
        # its results are destroyed every time the menu is hidden
        # e is the original contextmenu event, containing e.pageX and e.pageY (amongst other data)
        return {
            callback: (key, options) ->
                m = "clicked: " + key
                window.console && console.log(m) || alert(m)
            items: {
                "edit": {name: "Change Image", icon: "edit"}
            }
        }

})

class LayoutViewModel
    constructor: ->
        @header = ko.observable({
            text: 'ack'
        })
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
            @layoutItems(data.widgets)
        $.getJSON("/layout", callback)


ready = ->
    ko.applyBindings(new LayoutViewModel())
    console.log('starting knockout')

$(document).ready(ready)
$(document).on('page:load', ready)
