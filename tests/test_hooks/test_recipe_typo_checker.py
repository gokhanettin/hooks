# coding=utf-8

import os
import textwrap

from conans import tools

from tests.utils.test_cases.conan_client import ConanClientTestCase


class RecipeTypoCheckerTests(ConanClientTestCase):
    conanfile_basic = textwrap.dedent("""\
        from conans import ConanFile

        class AConan(ConanFile):
            name = "basic"
            version = "0.1"
            def package_info(self):
                self.cpp_info.defines = ["ACONAN"]
        """)
    conanfile_with_typos = textwrap.dedent("""\
        from conans import ConanFile

        class AConan(ConanFile):
            name = "basic"
            version = "0.1"

            export_sources = "OH_NO"

            require = "Hello/0.1@oh_no/stable"

            def requirement(self):
                self.requires("Hello/0.1@oh_no/stable")

            def package_info(self):
                self.cpp_info.defines = ["ACONAN"]
        """)

    def _get_environ(self, **kwargs):
        kwargs = super(RecipeTypoCheckerTests, self)._get_environ(**kwargs)
        kwargs.update({'CONAN_HOOKS': os.path.join(os.path.dirname(
            __file__), '..', '..', 'hooks', 'recipe_typo_checker')})
        return kwargs

    def test_conanfile_basic(self):
        tools.save('conanfile.py', content=self.conanfile_basic)
        output = self.conan(['export', '.', 'name/version@jgsogo/test'])
        self.assertNotIn("member looks like a typo", output)

    def test_conanfile_with_typos(self):
        tools.save('conanfile.py', content=self.conanfile_with_typos)
        output = self.conan(['export', '.', 'name/version@jgsogo/test'])
        recipe_typo_checker_output = textwrap.dedent("""\
            [HOOK - recipe_typo_checker.py] pre_export(): WARN: The 'export_sources' member looks like a typo. Similar to:
            [HOOK - recipe_typo_checker.py] pre_export(): WARN:     exports_sources
            [HOOK - recipe_typo_checker.py] pre_export(): WARN: The 'require' member looks like a typo. Similar to:
            [HOOK - recipe_typo_checker.py] pre_export(): WARN:     requires
            [HOOK - recipe_typo_checker.py] pre_export(): WARN: The 'requirement' member looks like a typo. Similar to:
            [HOOK - recipe_typo_checker.py] pre_export(): WARN:     requirements
            """)
        self.assertIn(recipe_typo_checker_output, output)
