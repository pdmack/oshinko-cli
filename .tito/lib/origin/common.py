from tito.common import run_command, get_latest_commit

def update_global_hash(spec_file):
    """
    Update the specfile to reflect the latest commit. A line
    with the following syntax is expected in the specfile:

    %global commit

    This line will be overwritten to add the git commit.
    """
    git_hash = get_latest_commit()
    update_commit = \
        "sed -i 's/^%global commit .*$/%global commit {0}/' {1}".format(
            git_hash,
            spec_file
        )
    run_command(update_commit)
