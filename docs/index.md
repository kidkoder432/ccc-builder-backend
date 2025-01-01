---
title: Home
layout: home
---
# Welcome to CCCBuilder documentation!

## What is CCCBuilder?

The most complex part of transfer admission from a community college to a university is fugirng out which courses will satisfy lower-division major requirements. In California, the [ASSIST](https://assist.org) tool helps students find articulation agreements with the schools they want to transfer to. However, these agreements are often cumbersome to follow, and in many cases, one's primary community college doesn't offer some critical courses required for admission. 

This is where CCCBuilder comes in. It allows students to select any number of UCs and CSUs to transfer to, along with their intended majors or minors at each school. After selecting their primary CCC (California Community College), CCCBuilder will help the student create a course plan that satisfies all of their major requirements. If some courses are not available at their primary CCC, CCCBuilder will find articulated courses at other CCCs. 

## Technical overview

- CCCBuilder's backend uses [FastAPI](https://fastapi.tiangolo.com) and runs on AWS Lambda using the [Lambda Web Adapter](https://github.com/awslabs/aws-lambda-web-adapter).
    *More details are available at the [backend page](/backend)*.

- CCCBuilder's frontend uses [React](https://reactjs.org/) and is hosted on [Vercel](https://vercel.com).
    *More details are available at the [frontend page](/frontend)*.

## Inspirations
- [Transfer Helper](https://transfer.lehuy.dev/) 
- [TransferVision](https://michaelrgarcia.github.io/transfer-vision/)

