'use strict';

/* App Module */

var pizzaclubApp = angular.module('pizzaclubApp', [
  'ngRoute',
  'pizzaclubControllers',
]).config(function($httpProvider) {
    $httpProvider.defaults.xsrfCookieName = 'csrftoken';
    $httpProvider.defaults.xsrfHeaderName = 'X-CSRFToken';
});

pizzaclubApp.config(['$routeProvider',
  function($routeProvider) {
    $routeProvider.
      when('/list', {
        templateUrl: 'views/list',
        controller: 'PizzaclubListCtrl'
      }).
      when('/details/:locationId', {
        templateUrl: '/static/bouncer.html',
        controller: 'PizzaclubDetailCtrl'
      }).
      when('/event/:eventId', {
        templateUrl: '/static/bouncer.html',
        controller: 'PizzaclubEventCtrl'
      }).
      otherwise({
        redirectTo: '/list'
      });
}]);
