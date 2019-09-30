<a name="unreleased"></a>
## [Unreleased]

### Bug Fixes
- Notebook launch path ([#472](https://github.com/illumidesk/illumidesk/issues/472))
- Lock traefik version
- Speed grader ([#466](https://github.com/illumidesk/illumidesk/issues/466))
- Install jupyterlab widgets extension ([#462](https://github.com/illumidesk/illumidesk/issues/462))
- Error when autograding second time
- Token login ([#381](https://github.com/illumidesk/illumidesk/issues/381))
- Permission denied when launching notebook
- nbgrader fixture for tests
- Assignment creation
- Revert js staticfiles ([#385](https://github.com/illumidesk/illumidesk/issues/385))
- Revert file_selector js file refactor ([#383](https://github.com/illumidesk/illumidesk/issues/383))
- Update incorrect js name ([#380](https://github.com/illumidesk/illumidesk/issues/380))
- Canvas auth ([#375](https://github.com/illumidesk/illumidesk/issues/375))
- Nginx ([#364](https://github.com/illumidesk/illumidesk/issues/364))
- Usage records ([#363](https://github.com/illumidesk/illumidesk/issues/363))
- Reroute from login to home when logged in ([#359](https://github.com/illumidesk/illumidesk/issues/359))
- File assignment test ordering
- File selection assignment creation url ([#349](https://github.com/illumidesk/illumidesk/issues/349))
- Teacher assignment file open
- Argument order ([#344](https://github.com/illumidesk/illumidesk/issues/344))
- Assignment retrieve error
- Server stats error ([#340](https://github.com/illumidesk/illumidesk/issues/340))
- Root dir ([#338](https://github.com/illumidesk/illumidesk/issues/338))
- Workspaces dir ([#335](https://github.com/illumidesk/illumidesk/issues/335))
- Project selection ([#334](https://github.com/illumidesk/illumidesk/issues/334))
- Assignment teacher project ([#333](https://github.com/illumidesk/illumidesk/issues/333))
- Tests
- Assignment file select
- Old assignments
- Add nbgrader exchange directory
- Prod migration fixes
- Container no longer exists exception
- Application delete in admin
- Assignment autograde score sums ([#302](https://github.com/illumidesk/illumidesk/issues/302))
- Assignment autograde
- Assignment grading resources
- Grader url
- Remove unnecessary update
- Canvas user account association  ([#276](https://github.com/illumidesk/illumidesk/issues/276))
- Teacher server launch
- Update ports to avoid conflicts with datadog ([#265](https://github.com/illumidesk/illumidesk/issues/265))
- Assignment copy file
- Change traefik ecs pool period so notebooks are available faster
- Server status ([#254](https://github.com/illumidesk/illumidesk/issues/254))
- Server status updates ([#253](https://github.com/illumidesk/illumidesk/issues/253))
- SNS and server launch ([#247](https://github.com/illumidesk/illumidesk/issues/247))
- LTI xml post request ([#243](https://github.com/illumidesk/illumidesk/issues/243))
- jupyter-lti build ([#237](https://github.com/illumidesk/illumidesk/issues/237))
- Dev raven config
- SNS servers status

### Code Refactoring
- Project permissions and autograding. ([#307](https://github.com/illumidesk/illumidesk/issues/307))

### Features
- lti names and roles ([#458](https://github.com/illumidesk/illumidesk/issues/458))
- Change grading path after autograding ([#396](https://github.com/illumidesk/illumidesk/issues/396))
- Update exchange folder config ([#392](https://github.com/illumidesk/illumidesk/issues/392))
- LTI 1.3 deep linking ([#374](https://github.com/illumidesk/illumidesk/issues/374))
- LTI mvp ([#373](https://github.com/illumidesk/illumidesk/issues/373))
- LTI v1.3 auth and modules ([#314](https://github.com/illumidesk/illumidesk/issues/314))
- Show only user owned project in canvas file selection
- UI updates ([#312](https://github.com/illumidesk/illumidesk/issues/312))
- Allow to select assignment file not only from release directory
- Show only release directory when selecting assignment file
- Add uuid to project and server admin list
- nbgader exchange directory ([#297](https://github.com/illumidesk/illumidesk/issues/297))
- Remove billing remnants
- Repo redo with terraform ([#212](https://github.com/illumidesk/illumidesk/issues/212))


<a name="v1.1.0"></a>
## [v1.1.0] - 2019-04-05

### Bug Fixes
- Remove sudo from buildspec.yml ([#196](https://github.com/illumidesk/illumidesk/issues/196))
- Fix AWS buildspec commands ([#195](https://github.com/illumidesk/illumidesk/issues/195))
- Admin owner filter repeats ([#190](https://github.com/illumidesk/illumidesk/issues/190))
- Fix unit tests ([#185](https://github.com/illumidesk/illumidesk/issues/185))
- Create new user with admin console ([#182](https://github.com/illumidesk/illumidesk/issues/182))
- Set OAuth2 application as optional when creating a new user ([#181](https://github.com/illumidesk/illumidesk/issues/181))
- Oauth application create fix ([#175](https://github.com/illumidesk/illumidesk/issues/175))
- Some tests fixes
- Some minor fixes for docker deployment
- Send assignment
- Canvas masquarade fix ([#159](https://github.com/illumidesk/illumidesk/issues/159))
- Minor post merge fixes ([#153](https://github.com/illumidesk/illumidesk/issues/153))
- Minor after merge fixes
- Canvas login issues ([#152](https://github.com/illumidesk/illumidesk/issues/152))
- Django 2 fixes ([#149](https://github.com/illumidesk/illumidesk/issues/149))
- Canvas instance relations fix ([#151](https://github.com/illumidesk/illumidesk/issues/151))
- Add fixes required by terraform blue/green deploy ([#140](https://github.com/illumidesk/illumidesk/issues/140))
- Use APP_DOMAIN instead of APP_SCHEME to format site name

### Code Refactoring
- Update tests for travis ([#201](https://github.com/illumidesk/illumidesk/issues/201))
- Remove ssh ([#170](https://github.com/illumidesk/illumidesk/issues/170))
- Remove host mounts ([#172](https://github.com/illumidesk/illumidesk/issues/172))
- Django 2 migration ([#146](https://github.com/illumidesk/illumidesk/issues/146))
- Remove getting started project ([#137](https://github.com/illumidesk/illumidesk/issues/137))

### Features
- Projects admin improvements
- Move db and redis to aws services ([#179](https://github.com/illumidesk/illumidesk/issues/179))
- Change celery broker from RabbitMQ to Redis ([#143](https://github.com/illumidesk/illumidesk/issues/143))
- Update repo to use changelog ([#139](https://github.com/illumidesk/illumidesk/issues/139))