import { get, set } from 'js-cookie';
export { Api } from './Api';
export { Payments } from './Payments';
export { Charts } from './examples/Charts';

// pass-through for Cookies API
export const Cookies = {
  get: get,
  set: set,
};
