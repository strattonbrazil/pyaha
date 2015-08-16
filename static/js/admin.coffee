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

class Menu
    constructor: (adminVM, menuData) ->        
        @_adminVM = adminVM
        @id = menuData.id
        @title = menuData.title

        @pages = ko.observableArray(menuData.pages)
        @pages.menuId = @id
        @orderChanged = (movedInfo) =>
            pageId = movedInfo.item.id
            @_movePage(pageId,
                movedInfo.sourceParent.menuId, movedInfo.sourceIndex,
                movedInfo.targetParent.menuId, movedInfo.targetIndex)

    _movePage: (pageId, srcMenuId, srcIndex, targetMenuId, targetIndex) ->
        $.ajax({
            type: "PATCH"
            url: "/pages/#{pageId}/order"
            data: {
                srcMenuId: srcMenuId,
                srcIndex: srcIndex,
                targetMenuId: targetMenuId,
                targetIndex: targetIndex
            }
            success: -> console.log('moved')
        })

    newPage: (viewmodel, event) =>
        @editPage()

    editPage: (page={}, event) =>
        if page.title?
            pageTitle = page.title
        else
            pageTitle = 'new_page'
            
        editDialog = $('#edit-page-dialog')

        editVM = {
            title: ko.observable(pageTitle)
            editMode: page.id?
            remove: =>
                removeDialogElement = document.getElementById('remove-dialog')
                removeDialog = $(removeDialogElement).dialog({
                    title: 'Delete Page'
                    modal: true
                    close: ->
                        ko.cleanNode(removeDialogElement)
                })

                removeVM = {
                    title: pageTitle
                    remove: =>
                        @_removePage(page.id)
                        removeDialog.dialog('close')
                        editDialog.dialog('close')
                }
                ko.applyBindings(removeVM, removeDialogElement)
        }

        if page.id?
            title = 'Edit Page'
        else
            title = 'New Page'

        dialogElement = document.getElementById('edit-page-dialog')
        ko.applyBindings(editVM, dialogElement)
        $(dialogElement).dialog({
            title: title
            modal: true
            minWidth: 800
            close: =>
                try
                    if page.id? # updating page
                        if editVM.title() isnt pageTitle
                            @_updatePage(page.id, { 'title' : editVM.title() })
                    else
                        @_createPage(editVM.title())
                finally
                    ko.cleanNode(dialogElement)
        })

    _updatePage: (pageId, updates) ->        
        $.ajax({
          type: "PATCH"
          url: "/page/#{pageId}"
          data: updates
          success: @_adminVM._requestPages
        })

    _createPage: (title) =>
        $.post("/pages", { title: title, menuId: @id }, @_adminVM._requestPages)

class AdminMenuViewModel
    constructor: ->
        @menus = ko.observableArray()
        #@pages = ko.observableArray()

        @_requestPages()

    _requestPages: =>
        parseResponse = (data) =>
            @menus.removeAll()
            for menuData in data.menus
                @menus.push(new Menu(@, menuData))
            #@pages(data.pages)

        $.getJSON("/menus", parseResponse)


        
    # loads a menu or creates a new one
    editMenu: (menu={}, event) =>
        if menu.title?
            menuTitle = menu.title
        else
            menuTitle = 'new_menu'
            
        editDialog = $('#edit-menu-dialog')
        
        editVM = {
            title: ko.observable(menuTitle)
            editMode: menu.id?
            remove: =>
                removeDialogElement = document.getElementById('remove-dialog')
                removeDialog = $(removeDialogElement).dialog({
                    title: 'Delete Menu'
                    modal: true
                    close: ->
                        ko.cleanNode(removeDialogElement)
                })
        
                removeVM = {
                    title: menuTitle
                    remove: =>
                        @_removeMenu(menu.id)
                        removeDialog.dialog('close')
                        editDialog.dialog('close')
                }
                ko.applyBindings(removeVM, removeDialogElement)
        }

        if menu.id?
            title = 'Edit Menu'
        else
            title = 'New Menu'

        dialogElement = document.getElementById('edit-menu-dialog')
        ko.applyBindings(editVM, dialogElement)
        $(dialogElement).dialog({
            title: title
            modal: true
            close: =>
                try
                    if menu.id? # updating a menu
                        if editVM.title() isnt menuTitle
                            @_updateMenuTitle(menu.id, editVM.title())
                    else
                        @_createMenu(editVM.title())
                finally
                    ko.cleanNode(dialogElement)
        })

    _updateMenuTitle: (id, title) ->
        $.ajax({
          type: "PATCH"
          url: "/menus/#{id}"
          data: { title: title }
          success: @_requestPages
        })

    _removeMenu: (id) ->
        $.ajax({
            type: "DELETE"
            url: "/menus/#{id}"
            success: @_requestPages
        })
                    
    newMenu: =>
        @editMenu()

    _createMenu: (title) =>
        $.post("/menus", { title: title }, @_requestPages)

    newPage: =>
        @editPage()

    _createPage: (title) =>
        $.post("/pages", { title: title }, @_requestPages)

class AdminImageViewModel
    constructor: (type) ->
        @_type = type

        @url = ko.observable("")
        @showSelector = ko.computed(=> @url() isnt "")
        
        @_requestImage()

    _requestImage: =>
        parseResponse = (data) =>
            @url(data.url)

        $.getJSON("/#{@_type}", parseResponse)

    uploadImage: ->
        console.log('here')

ready = ->
    #Dropzone.autoDiscover = false;
    #new Dropzone($("#header-dropzone").get(0));
    $("#header-dropzone").dropzone({ url: "/header" });
    ko.applyBindings(new AdminMenuViewModel(), document.getElementById('menu-content'))

    ko.applyBindings(new AdminImageViewModel('header'), document.getElementById('header-content'))

$(document).ready(ready)
$(document).on('page:load', ready)
