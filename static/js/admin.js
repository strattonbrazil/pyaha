// Generated by CoffeeScript 1.4.0
(function() {
  var AdminImageViewModel, AdminMenuViewModel, Menu, ready,
    __bind = function(fn, me){ return function(){ return fn.apply(me, arguments); }; };

  $.contextMenu({
    selector: '.right-click-edit',
    build: function($trigger, e) {
      console.log($trigger[0]);
      console.log($trigger);
      console.log(e);
      return {
        callback: function(key, options) {
          var m;
          m = "clicked: " + key;
          return window.console && console.log(m) || alert(m);
        },
        items: {
          "edit": {
            name: "Change Image",
            icon: "edit"
          }
        }
      };
    }
  });

  Menu = (function() {

    function Menu(adminVM, menuData) {
      this._createPage = __bind(this._createPage, this);

      this.editPage = __bind(this.editPage, this);

      this.newPage = __bind(this.newPage, this);

      var _this = this;
      this._adminVM = adminVM;
      this.id = menuData.id;
      this.title = menuData.title;
      this.pages = ko.observableArray(menuData.pages);
      this.pages.menuId = this.id;
      this.orderChanged = function(movedInfo) {
        var pageId;
        pageId = movedInfo.item.id;
        return _this._movePage(pageId, movedInfo.sourceParent.menuId, movedInfo.sourceIndex, movedInfo.targetParent.menuId, movedInfo.targetIndex);
      };
    }

    Menu.prototype._movePage = function(pageId, srcMenuId, srcIndex, targetMenuId, targetIndex) {
      return $.ajax({
        type: "PATCH",
        url: "/pages/" + pageId + "/order",
        data: {
          srcMenuId: srcMenuId,
          srcIndex: srcIndex,
          targetMenuId: targetMenuId,
          targetIndex: targetIndex
        },
        success: function() {
          return console.log('moved');
        }
      });
    };

    Menu.prototype.newPage = function(viewmodel, event) {
      return this.editPage();
    };

    Menu.prototype.editPage = function(page, event) {
      var dialogElement, editDialog, editVM, pageTitle, title,
        _this = this;
      if (page == null) {
        page = {};
      }
      if (page.title != null) {
        pageTitle = page.title;
      } else {
        pageTitle = 'new_page';
      }
      editDialog = $('#edit-page-dialog');
      editVM = {
        title: ko.observable(pageTitle),
        editMode: page.id != null,
        remove: function() {
          var removeDialog, removeDialogElement, removeVM;
          removeDialogElement = document.getElementById('remove-dialog');
          removeDialog = $(removeDialogElement).dialog({
            title: 'Delete Page',
            modal: true,
            close: function() {
              return ko.cleanNode(removeDialogElement);
            }
          });
          removeVM = {
            title: pageTitle,
            remove: function() {
              _this._removePage(page.id);
              removeDialog.dialog('close');
              return editDialog.dialog('close');
            }
          };
          return ko.applyBindings(removeVM, removeDialogElement);
        }
      };
      if (page.id != null) {
        title = 'Edit Page';
      } else {
        title = 'New Page';
      }
      dialogElement = document.getElementById('edit-page-dialog');
      ko.applyBindings(editVM, dialogElement);
      return $(dialogElement).dialog({
        title: title,
        modal: true,
        minWidth: 800,
        close: function() {
          try {
            if (page.id != null) {
              if (editVM.title() !== pageTitle) {
                return _this._updatePage(page.id, {
                  'title': editVM.title()
                });
              }
            } else {
              return _this._createPage(editVM.title());
            }
          } finally {
            ko.cleanNode(dialogElement);
          }
        }
      });
    };

    Menu.prototype._updatePage = function(pageId, updates) {
      return $.ajax({
        type: "PATCH",
        url: "/page/" + pageId,
        data: updates,
        success: this._adminVM._requestPages
      });
    };

    Menu.prototype._createPage = function(title) {
      return $.post("/pages", {
        title: title,
        menuId: this.id
      }, this._adminVM._requestPages);
    };

    return Menu;

  })();

  AdminMenuViewModel = (function() {

    function AdminMenuViewModel() {
      this._createPage = __bind(this._createPage, this);

      this.newPage = __bind(this.newPage, this);

      this._createMenu = __bind(this._createMenu, this);

      this.newMenu = __bind(this.newMenu, this);

      this.editMenu = __bind(this.editMenu, this);

      this._requestPages = __bind(this._requestPages, this);
      this.menus = ko.observableArray();
      this._requestPages();
    }

    AdminMenuViewModel.prototype._requestPages = function() {
      var parseResponse,
        _this = this;
      parseResponse = function(data) {
        var menuData, _i, _len, _ref, _results;
        _this.menus.removeAll();
        _ref = data.menus;
        _results = [];
        for (_i = 0, _len = _ref.length; _i < _len; _i++) {
          menuData = _ref[_i];
          _results.push(_this.menus.push(new Menu(_this, menuData)));
        }
        return _results;
      };
      return $.getJSON("/menus", parseResponse);
    };

    AdminMenuViewModel.prototype.editMenu = function(menu, event) {
      var dialogElement, editDialog, editVM, menuTitle, title,
        _this = this;
      if (menu == null) {
        menu = {};
      }
      if (menu.title != null) {
        menuTitle = menu.title;
      } else {
        menuTitle = 'new_menu';
      }
      editDialog = $('#edit-menu-dialog');
      editVM = {
        title: ko.observable(menuTitle),
        editMode: menu.id != null,
        remove: function() {
          var removeDialog, removeDialogElement, removeVM;
          removeDialogElement = document.getElementById('remove-dialog');
          removeDialog = $(removeDialogElement).dialog({
            title: 'Delete Menu',
            modal: true,
            close: function() {
              return ko.cleanNode(removeDialogElement);
            }
          });
          removeVM = {
            title: menuTitle,
            remove: function() {
              _this._removeMenu(menu.id);
              removeDialog.dialog('close');
              return editDialog.dialog('close');
            }
          };
          return ko.applyBindings(removeVM, removeDialogElement);
        }
      };
      if (menu.id != null) {
        title = 'Edit Menu';
      } else {
        title = 'New Menu';
      }
      dialogElement = document.getElementById('edit-menu-dialog');
      ko.applyBindings(editVM, dialogElement);
      return $(dialogElement).dialog({
        title: title,
        modal: true,
        close: function() {
          try {
            if (menu.id != null) {
              if (editVM.title() !== menuTitle) {
                return _this._updateMenuTitle(menu.id, editVM.title());
              }
            } else {
              return _this._createMenu(editVM.title());
            }
          } finally {
            ko.cleanNode(dialogElement);
          }
        }
      });
    };

    AdminMenuViewModel.prototype._updateMenuTitle = function(id, title) {
      return $.ajax({
        type: "PATCH",
        url: "/menus/" + id,
        data: {
          title: title
        },
        success: this._requestPages
      });
    };

    AdminMenuViewModel.prototype._removeMenu = function(id) {
      return $.ajax({
        type: "DELETE",
        url: "/menus/" + id,
        success: this._requestPages
      });
    };

    AdminMenuViewModel.prototype.newMenu = function() {
      return this.editMenu();
    };

    AdminMenuViewModel.prototype._createMenu = function(title) {
      return $.post("/menus", {
        title: title
      }, this._requestPages);
    };

    AdminMenuViewModel.prototype.newPage = function() {
      return this.editPage();
    };

    AdminMenuViewModel.prototype._createPage = function(title) {
      return $.post("/pages", {
        title: title
      }, this._requestPages);
    };

    return AdminMenuViewModel;

  })();

  AdminImageViewModel = (function() {

    function AdminImageViewModel(type) {
      this._requestImage = __bind(this._requestImage, this);

      var _this = this;
      this._type = type;
      this.url = ko.observable("");
      this.showSelector = ko.computed(function() {
        return _this.url() !== "";
      });
      this._requestImage();
    }

    AdminImageViewModel.prototype._requestImage = function() {
      var parseResponse,
        _this = this;
      parseResponse = function(data) {
        return _this.url(data.url);
      };
      return $.getJSON("/" + this._type, parseResponse);
    };

    AdminImageViewModel.prototype.uploadImage = function() {
      return console.log('here');
    };

    return AdminImageViewModel;

  })();

  ready = function() {
    ko.applyBindings(new AdminMenuViewModel(), document.getElementById('menu-content'));
    return ko.applyBindings(new AdminImageViewModel('header'), document.getElementById('header-content'));
  };

  $(document).ready(ready);

  $(document).on('page:load', ready);

}).call(this);
