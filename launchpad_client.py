#!/usr/bin/env python
#-*- coding: utf-8 -*-

# Copyright (c) 2015 Mirantis Inc.
#
# Licensed under the GNU General Public License, Version 2.0

import os

from launchpadlib.launchpad import Launchpad
from launchpadlib.launchpad import uris


class launchpad_client(object):

    def __init__(self, project):

        lp_cache_dir = os.path.expanduser(
            os.environ.get('LAUNCHPAD_CACHE_DIR',
                           '~/.launchpadlib/cache'))

        lp_creds_filename = os.path.expanduser(
            os.environ.get('LAUNCHPAD_CREDS_FILENAME',
                           '~/.launchpadlib/creds'))

        self.Launchpad = Launchpad.login_with(
            project.lower(),
            uris.LPNET_SERVICE_ROOT,
            lp_cache_dir,
            credentials_file=lp_creds_filename)

        self.Project = None
        self.Bug = None
        self.Tasks = []

        self.project(project.lower())

    @property
    def launchpad(self):
        return self.Launchpad

    def project(self, project=None):
        if project is not None:
            try:
                self.Project = self.launchpad.projects[project]
            except KeyError:
                print "Can't load project '{}' information".format(project)
                exit()
        return self.Project

    def bug(self, bug_id=None):
        if bug_id is not None:
            if self.Bug is None or self.Bug.id != bug_id:
                try:
                    self.Bug = self.launchpad.bugs[bug_id]
                except KeyError:
                    print "Can't load bug #{} information".format(bug_id)
                    exit()
        return self.Bug

    def tasks(self, bug_id=None):
        if bug_id is not None:
            self.Tasks = self.bug(bug_id).bug_tasks
        return self.Tasks

    def create_bug(self, title, description, **properties):
        bug = self.launchpad.bugs.createBug(target=self.project().self_link,
                                            title=title,
                                            description=description)
        self.update_bug(bug.id, **properties)
        return bug

    def update_bug(self, bug_id=None, **properties):
        bug = self.bug(bug_id)
        updated = False
        for p in ['title', 'description', 'private', 'tags']:
            if p in properties:
                setattr(bug, p, properties[p])
                updated = True
        if 'affects_project' in properties:
            self.bug().addTask(
                target=self.launchpad.projects[properties['affects_project']])
        if updated:
            bug.lp_save()

        for task in self.tasks(bug_id):
            self.update_task(task, **properties)

        return bug

    def update_task(self, task, **properties):
        updated = False
        if task.target.name in properties['affects_only']:
            if 'assignee' in properties:
                properties['assignee'] = \
                    self.launchpad.people(properties['assignee'])
            if 'milestone' in properties:
                properties['milestone'] = \
                    self.project().getMilestone(name=properties['milestone'])
            for p in ['status', 'importance', 'milestone', 'assignee']:
                if p in properties:
                    setattr(task, p, properties[p])
                    updated = True
            if updated:
                task.lp_save()

    def add_comment(self, comment, bug_id=None, **properties):
        for p in [task.target.name for task in self.tasks(bug_id)]:
            if p in properties['affects_only']:
                return self.bug(bug_id).newMessage(content=comment)
