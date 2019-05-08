#!/usr/bin/env node
import 'source-map-support/register';
import cdk = require('@aws-cdk/cdk');
import { IllumiDeskStackStack } from '../lib/illumi_desk_stack-stack';

const app = new cdk.App();

new IllumiDeskStackStack(app, 'IllumiDeskStackStack');