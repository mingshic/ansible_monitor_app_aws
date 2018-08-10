# .bash_profile

# Get the aliases and functions
if [ -f ~/.bashrc ]; then
	. ~/.bashrc
fi

# User specific environment and startup programs

PATH=$PATH:$HOME/.local/bin:$HOME/bin

export PATH

umask 022
export ORACLE_HOSTNAME={{ ansible_hostname }}
export ORACLE_BASE=/{{ oracle_base_begin }}/app/oracle
export ORACLE_HOME=$ORACLE_BASE/product/{{ oracle_version }}/{{ oracle_db_number }}
export ORACLE_SID={{ oracle_sid }}
export PATH=.:$ORACLE_HOME/bin:$ORACLE_HOME/OPatch:$ORACLE_HOME/jdk/bin:$PATH
export LC_ALL="en_US"
export LANG="en_US"
export NLS_LANG="SIMPLIFIED CHINESE_CHINA.ZHS16GBK"
#export NLS_DATE_FORMAT="YYYY-MM-DD HH24:MI:SS"
