'use strict';

/* Controllers */

var pizzaclubControllers = angular.module('pizzaclubControllers', []);

pizzaclubControllers.controller('PizzaclubListCtrl', ['$scope', '$routeParams',
  function($scope, Pizzaclub) {
  }]);

pizzaclubControllers.controller('PizzaclubDetailCtrl', ['$scope', '$routeParams',
  function($scope, $routeParams) {
      $scope.dataUrl = 'views/details?id='+$routeParams.locationId;
      
  }]);

pizzaclubControllers.controller('PizzaclubEventCtrl', ['$scope', '$http', '$routeParams',
  function($scope, $http, $routeParams) {
      $scope.dataUrl = 'views/event?id='+$routeParams.eventId;

      init();

      function setInScope(data) {
          $scope.event_id = data.event_id;
          $scope.vote_list = data.vote_list;
          $scope.id_crust = data.id_crust;
          $scope.id_sauce = data.id_sauce;
          $scope.id_service = data.id_service;
          $scope.id_creativity = data.id_creativity;
          $scope.id_overall = data.id_overall;
      }

      function init() {
          $http.post("views/vote/", {event_id : $routeParams.eventId})
              .success(function(data, status, headers, config){
                  setInScope(data);
              });
      }          

      $scope.submitVote = function(id_crust, id_sauce, id_service, id_creativity, id_overall) {
          // Verify that the values exist and are valid
          if ((id_crust >= 0 || id_crust <= 5) &&
              (id_sauce >= 0 || id_sauce <= 5) &&
              (id_service >= 0 || id_service <= 5) &&
              (id_creativity >= 0 || id_creativity <= 5) &&
              (id_overall >= 0 || id_overall <= 5)) {
              $http.post("views/vote/", {event_id : $scope.event_id,
                                         vote: {
                                             crust: id_crust,
                                             sauce: id_sauce,
                                             service: id_service,
                                             creativity: id_creativity,
                                             overall: id_overall,
                                         },
                                        })
                  .success(function(data, status, headers, config){
                      setInScope(data);
                  });
          } else {
              alert('You have incorrect values')
          }
      }
  }]);

