'use strict';
import React from "react";
import ReactDOM from "react-dom";
import {API_ROOT} from "./Const";
import {getAction} from '../Api';


class EmployeeTableRow extends React.Component {
    render() {
        return (
            <tr>
                <td>{this.props.name}</td>
                <td>{this.props.department}</td>
                <td>{this.props.salary}</td>
                <td className="has-text-right">
                    <a onClick={() => this.props.edit(this.props.index)}>
                        <span>Edit</span>
                    </a>
                    <a style={{'marginLeft': '1em'}} onClick={() => this.props.delete(this.props.index)}>
                        <span>Delete</span>
                    </a>
                </td>
            </tr>
        );
    }
}

class EditAddEmployeeWidget extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            name: props.activeObject ? props.activeObject.name : "",
            department: props.activeObject ? props.activeObject.department : EMPLOYEE_DEPARTMENT_CHOICES[0].id,
            salary: props.activeObject ? props.activeObject.salary : "",
            editMode: Boolean(props.activeObject),
        };
        this.nameChanged = this.nameChanged.bind(this);
        this.departmentChanged = this.departmentChanged.bind(this);
        this.salaryChanged = this.salaryChanged.bind(this);
        this.save = this.save.bind(this);
        this.cancel = this.cancel.bind(this);
    }

    render() {
        return (
            <div>
                {this.renderDetails()}
            </div>
        )
    }

    renderDetails() {
        return (
            <section className="section app-card">
                <form>
                    <h2 className="subtitle">Employee Details</h2>
                    <div className="field">
                        <label className="label">Name</label>
                        <div className="control">
                            <input className="input" type="text" placeholder="Michael Scott"
                                   onChange={this.nameChanged} value={this.state.name}>
                            </input>
                        </div>
                        <p className="help">Your employee's name.</p>
                    </div>
                    <div className="field">
                        <div className="control">
                            <label className="label">Department</label>
                            <div className="select">
                                <select onChange={this.departmentChanged} value={this.state.department}>
                                    { EMPLOYEE_DEPARTMENT_CHOICES.map(
                                        (department, index) => <option key={department.id} value={department.id}>{department.name}</option>
                                    )}
                              </select>
                          </div>
                      </div>
                      <p className="help">What department your employee belongs to.</p>
                    </div>
                    <div className="field">
                        <div className="control">
                            <label className="label">Salary</label>
                            <input className="input" type="number" min="0" placeholder="50000"
                                   onChange={this.salaryChanged} value={this.state.salary}>
                            </input>
                      </div>
                      <p className="help">Your employee's annual salary.</p>
                    </div>
                    <div className="field is-grouped">
                        <div className="control">
                            <button className={`button is-primary ${this.state.editMode ? 'is-outlined' : ''}`}
                                    onClick={this.save}>
                              <span className="icon is-small">
                                  <i className={`fa ${this.state.editMode ? 'fa-check' : 'fa-plus'}`}></i>
                              </span>
                                <span>{this.state.editMode ? 'Save Employee' : 'Add Employee'}</span>
                            </button>
                        </div>
                        <div className="control">
                            <button className="button is-text" onClick={this.cancel}>
                                <span>Cancel</span>
                            </button>
                        </div>
                    </div>
                </form>
            </section>
        );
    }

    nameChanged(event) {
        this.setState({name: event.target.value});
    }

    departmentChanged(event) {
        this.setState({department: event.target.value});
    }

    salaryChanged(event) {
        this.setState({salary: event.target.value});
    }

    save(event) {
        this.props.save(this.props.activeObject, this.state.name, this.state.department, this.state.salary);
        event.preventDefault();
    }

    cancel(event) {
        this.props.cancel();
        event.preventDefault();
    }
}



class EmployeeApplication extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            loading: true,
            editMode: false,
            employees: [],
            activeObject: null,
        }
        this._initializeData = this._initializeData.bind(this);
        this._cancelEdit = this._cancelEdit.bind(this);
        this._editEmployee = this._editEmployee.bind(this);
        this._saveEmployee = this._saveEmployee.bind(this);
    };

    componentDidMount() {
        this.setState({
            client: client,
        });
        let action = getAction(API_ROOT, ["employees", "list"]);
        client.action(window.schema, action).then((result) => {
            this._initializeData(result.results);
        });
    }

    _initializeData(employees) {
        this.setState({
            loading: false,
            employees: employees,
        });
    }

    render () {
        if (this.state.loading) {
            return 'Loading data...';
        } else if (this.state.editMode) {
            return (
                <EditAddEmployeeWidget
                    save={this._saveEmployee}
                    cancel={this._cancelEdit}
                    activeObject={this.state.activeObject}
                />

            );
        }
        if (this.state.employees.length === 0) {
            return this.renderEmpty();
        } else {
            return this.renderList();
        }
    }

    renderEmpty() {
        return (
            <section className="section app-card">
                <div className="columns">
                    <div className="column is-one-third">
                        <img alt="Nothing Here" src={STATIC_FILES.undraw_empty}/>
                    </div>
                    <div className="column is-two-thirds">
                        <h1 className="title is-4">No Employees Yet!</h1>
                        <h2 className="subtitle">Create your first employee below to get started.</h2>

                        <p>
                            <a className="button is-primary" onClick={() => this._newEmployee()}>
                                <span className="icon is-small"><i className="fa fa-plus"></i></span>
                                <span>Create Employee</span>
                            </a>
                        </p>
                    </div>
                </div>
            </section>
        );
    }

    renderList() {
        return (
               <section className="section app-card">
                <h1 className="subtitle">All Employees</h1>
                <table className="table is-striped is-fullwidth">
                    <thead>
                    <tr>
                        <th>Name</th>
                        <th>Department</th>
                        <th>Salary</th>
                        <th></th>
                    </tr>
                    </thead>
                    <tbody>
                    {
                        this.state.employees.map((employee, index) => {
                            // https://stackoverflow.com/a/27009534/8207
                            return <EmployeeTableRow key={employee.id} index={index} {...employee}
                                                 edit={(index) => this._editEmployee(index)}
                                                 delete={(index) => this._deleteEmployee(index)}
                            />;
                        })
                    }
                    </tbody>
                </table>
                <button className="button is-primary is-outlined" onClick={() => this._newEmployee()}>
                <span className="icon is-small">
                    <i className="fa fa-plus"></i>
                </span>
                    <span>Add Employee</span>
                </button>
            </section>
        );
    }

    _newEmployee() {
        this.setState({
            editMode: true,
        });
    }

    _editEmployee(index) {
        this.setState({
            activeObject: this.state.employees[index],
            editMode: true,
        });
    }

    _deleteEmployee(index) {
        let action = getAction(API_ROOT, ["employees", "delete"]);
        let params = {id: this.state.employees[index].id};
        this.state.client.action(window.schema, action, params).then((result) => {
            this.state.employees.splice(index, 1);
            this.setState({
                employees: this.state.employees
            });
        });
    }

    _saveEmployee(employee, name, department, salary) {
        let params = {
            name: name,
            department: department,
            salary: salary,
        };
        if (Boolean(employee)) {
            params['id'] = employee.id;
            let action = getAction(API_ROOT, ["employees", "partial_update"]);
            this.state.client.action(window.schema, action, params).then((result) => {
                // find the appropriate item in the list and update in place
                for (var i = 0; i < this.state.employees.length; i++) {
                    if (this.state.employees[i].id === result.id) {
                        this.state.employees[i] = result;
                    }
                }
                this.setState({
                    editMode: false,
                    activeObject: null,
                    employees: this.state.employees,
                });
            }).catch((error) => {
                console.log("Error: ", error);
             });
        } else {
            let action = getAction(API_ROOT, ["employees", "create"]);
            this.state.client.action(window.schema, action, params).then((result) => {
                this.state.employees.push(result);
                this.setState({
                    editMode: false,
                    activeObject: null,
                    employees: this.state.employees,
                });
            });
        }
    }

    _cancelEdit(name, value) {
        this.setState({
            editMode: false,
            activeObject: null,
        });
    }

}


let auth = new coreapi.auth.SessionAuthentication({
    csrfCookieName: 'csrftoken',
    csrfHeaderName: 'X-CSRFToken'
});
let client = new coreapi.Client({auth: auth});
let domContainer = document.querySelector('#crud-home');
domContainer ? ReactDOM.render(
    <EmployeeApplication/>
    , domContainer) : null;
