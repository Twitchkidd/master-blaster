#

# reporting #
# * Text! * #


def intro():
    """Print the license, intro blurb, and token blurb!"""
    licenseText = """
      master-blaster: Rename primary branches of code repositories.
      Copyright (C) 2020  Gareth Field field.gareth@gmail.com

      This program is free software: you can redistribute it and/or modify
      it under the terms of the GNU General Public License as published by
      the Free Software Foundation, either version 3 of the License, or
      (at your option) any later version.

      This program is distributed in the hope that it will be useful,
      but WITHOUT ANY WARRANTY; without even the implied warranty of
      MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
      GNU General Public License for more details.

      You should have received a copy of the GNU General Public License
      along with this program.  If not, see <https://www.gnu.org/licenses/>.
  """
    print(licenseText)

    introText = """
      Welcome to master-blaster! This program batch renames primary branches
      for GitHub users! We'll go through the options before making any changes!
  """
    print(introText)

    tokenExplanation = """
      Also, GitHub is deprecating password-based token generation! This is great for
      security, it just means you're going to have to go to GitHub.com and
      come back with an access token to run the program, and it's a couple of steps,
      still faster than doing each manually if you have a bunch of repos, though.
      Thank you!
  """
    print(tokenExplanation)


def repoTypesBlurb():
    """Explain all repos, owner, public/private."""


def denoument():
    print("Thank you for using master-blaster!\n")
    print("Check the log file at ./info.log for details!")
