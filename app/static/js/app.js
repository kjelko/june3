angular.module('June3App', ['ngMaterial', 'duScroll'])
  .controller('PageController', [
        '$window', '$rootScope', '$http', PageController
  ])
  .controller('AdminController', [
        '$rootScope', '$http', '$mdToast', AdminController
  ])
  .config(['$mdThemingProvider', config])
  .value('duScrollOffset', 54);
