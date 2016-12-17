var config = function($mdThemingProvider, $interpolateProvider) {

  $interpolateProvider.startSymbol('%%').endSymbol('%%');

  $mdThemingProvider.definePalette('june3Primary', 
    $mdThemingProvider.extendPalette('green', {
      '600': '#adc67b'
    }));
  
  $mdThemingProvider.definePalette('june3Accent', 
    $mdThemingProvider.extendPalette('orange', {
      '600': '#df862d',
      'A700': '#fecb9c',
      'contrastLightColors': ['600']
    }));
  
  $mdThemingProvider.theme('default')
    .primaryPalette('june3Primary', {'default': '600'})
    .accentPalette('june3Accent', {'default': '600'})
    .warnPalette('red', {'default': '600'});
};
