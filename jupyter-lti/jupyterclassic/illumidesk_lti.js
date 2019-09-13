define([
    'base/js/namespace'
    ], function(
        Jupyter
    ) {
        'use strict';

        // Get the assignment id from the address bar
        var get_assignment_id = function () {
            var query = new URLSearchParams(window.location.search);
            var assignment_id = query.get('assignment_id');
            if (!assignment_id) {
                return 'error';
            }
            else { return assignment_id }
        }

        // Get url from browser's address bar
        var get_url = function (assignment_id) {
            var proto = window.location.protocol;
            var parts = window.location.pathname.split('/');
            var version = parts[1];
            var serverName = parts[6];
            var projectName = parts[4];
            var accountName = parts[2];
            return proto + "//" + window.location.host + "/" + version + "/" + accountName + "/projects/" + projectName + "/servers/" + serverName + "/lti/assignment/" + assignment_id + "/";
        }

        var submit_assignment = function () {
            var assignment_id = get_assignment_id()
            if (assignment_id == 'error') { 
                alert('Error: invalid assignment id. Please open your assignment from the LMS course assignment link.')
                return;
            }
            var submit_url = get_url(assignment_id)
            fetch(submit_url, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json;charset=utf-8' },
                referrerPolicy: 'no-referrer'
            }).then(function (response) {
                if (!response.ok) {
                    alert('Error: there was an error processing your assignment submission request.')
                    return;
                }
                else {
                    alert("Success: your assignment has been successfully submitted.")
                }
            })
        }

        // Submit assignment button
        var submit_assignment_button = function () {
            Jupyter.toolbar.add_buttons_group([
                Jupyter.keyboard_manager.actions.register ({
                    'help': 'Submit assignment',
                    'icon' : 'fa-paper-plane',
                    'handler': submit_assignment
                },  'add-default-cell', 'Default cell')
            ])
        }

        // Run on start
        function load_ipython_extension() {
            submit_assignment_button();
        }

        return {
            load_ipython_extension: load_ipython_extension
        };
});
