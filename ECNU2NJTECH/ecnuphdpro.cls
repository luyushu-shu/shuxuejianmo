% 论文版面要求:
% 统一按 word 格式A4纸（页面设置按word默认值）编排、打印、制作。
% 正文内容字体为宋体；字号为小4号；字符间距为标准；行距为25磅(约0.88175cm)。
%
\NeedsTeXFormat{LaTeX2e}[1999/12/01]
\ProvidesClass{ecnuphdpro}[2025/07/03 template for NJTECH PhD (Professional)]

%%%% basic document class
\LoadClassWithOptions{ctexbook}

%%%%% first page style of chapter
\def\ps@firstpage{\ps@plain
  \def\@oddfoot{}%
  \let\@evenfoot\@oddfoot
  \def\@oddhead{}%
  \let\@evenhead\@oddhead % in case a chapter starts on a left-hand page
}

%%%%% layout
%\RequirePackage[a4paper,includehead,includefoot]{geometry}
\RequirePackage[a4paper]{geometry}
\geometry{left=3.17cm,right=3.17cm,top=3.54cm,bottom=3.54cm,headsep=1cm,footskip=15mm}

\setlength{\parindent}{2em}
\setlength{\parskip}{0.5em}

%%%%% ctex
%\RequirePackage[UTF8,10pt,heading=true,cap]{ctex}
\ctexset{%
  contentsname={\zihao{3}目\ \ 录},
  listfigurename={插\ 图\ 目\ 录},
  listtablename={表\ 格\ 目\ 录},
 % bibname={\centerline{参\ 考\ 文\ 献}},
  chapter={name={第,章},
           number=\chinese{chapter},
           nameformat={\zihao{3}\bfseries},
           titleformat={\zihao{3}\bfseries},
           beforeskip={-10pt},
           afterskip={20pt}
           },
  section={format=\raggedright,
           nameformat={\zihao{4}\bfseries},
           titleformat={\zihao{4}\bfseries},
           afterskip={1ex plus 0.2ex}
           },
  subsection={format=\raggedright,
           nameformat={\zihao{-4}\bfseries},
           titleformat={\zihao{-4}\bfseries},
           afterskip={0.5ex plus 0.1ex}
           }
}

%%%%% default font
\setmainfont{Times New Roman}
%\setCJKmainfont[BoldFont={Microsoft YaHei},ItalicFont={KaiTi}]{SimSun}
%\setCJKsansfont{KaiTi}
%\setCJKmonofont{KaiTi}
\newcommand{\song}{\songti}
\newcommand{\hei}{\heiti}
\newcommand{\kai}{\kaishu}
\newcommand{\you}{\youyuan}
\setCJKfamilyfont{STSong}{STZhongsong}\newcommand{\STSong}{\CJKfamily{STSong}}

%%%% math and references
\RequirePackage{amsmath}
\RequirePackage{amssymb}
\RequirePackage{amsfonts}
\RequirePackage{bm}
  \allowdisplaybreaks[4]
  \numberwithin{equation}{chapter}
\RequirePackage[numbers,square,sort&compress]{natbib}
  \setlength{\bibsep}{1.0ex}

%%%%% graphics and color
\RequirePackage{graphicx}
%\RequirePackage{subfig}

\RequirePackage{xcolor}

%%%%% index
\RequirePackage{makeidx}\makeindex   % 索引


%%%%% caption
\RequirePackage[margin=2em,labelsep=space,skip=0.5ex]{caption}
\DeclareCaptionFormat{mycaption}{{\heiti\color{blue} #1}#2{\kaishu #3}}
\captionsetup{format=mycaption,tablewithin=chapter,figurewithin=chapter}

%%%%% contents
%\setcounter{secnumdepth}{3}
%\setcounter{tocdepth}{3}
\RequirePackage{titletoc}
\contentsmargin{2em}
\titlecontents{chapter}[4em]%
  {\vspace*{1ex}\heiti}%
  {\color{blue}\contentslabel{4em}}%
  {\hspace*{-4em}}%
  {\hspace{5pt}\titlerule*[8pt]{.}\bfseries\contentspage}%
  [\addvspace{-1.0ex}]
\titlecontents{section}
  [4em]%
  {\vspace*{0ex}}%
  {\color{blue}\contentslabel[\thecontentslabel]{2.5em}}%
  {\hspace*{-1.8em}}%
  {\hspace{5pt}\titlerule*[8pt]{.}\contentspage}%
  [\addvspace{-1.5ex}]
\titlecontents{subsection}
  [7.0em]%
  {\vspace*{-0.2ex}}%
  {\color{blue}\contentslabel[\thecontentslabel]{3.0em}}%
  {}%
  {\hspace{5pt}\titlerule*[5pt]{.}\contentspage}%
  [\addvspace{-1.3ex}]

%%%%% Theorems
\usepackage[amsmath,thref,thmmarks,hyperref]{ntheorem}
\theorempostskipamount0em
\theoremstyle{plain}
\theoremheaderfont{\normalfont\heiti\color{black}}
\theorembodyfont{\normalfont\kaishu\color{black}}
\theoremindent0em
\theoremseparator{\hspace{0.2em}}
\theoremnumbering{arabic}
\newtheorem{theorem}{定理}[chapter]
\newtheorem{lemma}[theorem]{引理}
\newtheorem{corollary}[theorem]{推论}
\newtheorem{proposition}[theorem]{命题}
\newtheorem{property}[theorem]{性质}
\newtheorem{definition}{定义}[chapter]
\newtheorem{remark}{注记}[chapter]
%
%\theoremheaderfont{\normalfont\itshape\color{blue}}
\theorembodyfont{\normalfont\rmfamily\color{black}}
\newtheorem{example}{例}[chapter]

\newenvironment{proof}[1][证明]%
  {\par\noindent\normalfont{\bfseries\color{blue} #1.} \upshape}
  {\mbox{}\hfill\scalebox{1.2}{\ensuremath{\Box}}\medskip}

%%%%% heading
\RequirePackage{fancyhdr}
\pagestyle{fancy}
\fancyhf{}  % 清除以前对页眉页脚的设置
\fancyhead[CO,CE]{南京工业大学博士专业学位论文}
\fancyfoot[RO,LE]{{\thepage}}
%\newcommand{\makeheadrule}{%% 定义页眉与正文间双隔线
%  \makebox[0pt][l]{\rule[.7\baselineskip]{\headwidth}{0.3pt}}%0.4
%  \rule[0.85\baselineskip]{\headwidth}{1.0pt}\vskip-.8\baselineskip}
%\renewcommand{\headrule}{%
%  {\if@fancyplain\let\headrulewidth\plainheadrulewidth\fi\makeheadrule}}
%\renewcommand{\chaptermark}[1]{\markboth{\CTEXthechapter \ #1}{}}
%\renewcommand{\sectionmark}[1]{\markright{\thesection \ #1}{}}
%\fancyhead[RO,LE]{{\small\songti\rightmark}}     % 节标题
%\fancyhead[RE]{{\small\songti\leftmark}}      % 章标题
%\fancyhead[RO,LE]{$\cdot$ {\small\thepage} $\cdot$}

%%%% tabular
\RequirePackage{booktabs} % toprule, midrule, bottomrule
\RequirePackage{varwidth} % 可变宽度的 parbox

%%%%% float
\RequirePackage{float}

%%%%% underline
\RequirePackage[normalem]{ulem}
\def\ULthickness{1pt}

%%%%% cover
\def\class#1{\def\@class{#1}}\def\@class{}
\def\security#1{\def\@security{#1}}\def\@security{}
\def\graduateyear#1{\def\@graduateyear{#1}}\def\@graduateyear{}
\def\ctitle#1{\def\@ctitle{#1}}\def\@ctitle{}
\def\caffil#1{\def\@caffil{#1}}\def\@caffil{}
\def\cmajor#1{\def\@cmajor{#1}}\def\@cmajor{}
\def\cdirection#1{\def\@cdirection{#1}}\def\@cdirection{}
\def\cauthor#1{\def\@cauthor{#1}}\def\@cauthor{}
\def\studentid#1{\def\@studentid{#1}}\def\@studentid{}
\def\csupervisor#1{\def\@csupervisor{#1}}\def\@csupervisor{}
\def\cdate#1{\def\@cdate{#1}}\def\@cdate{}
\def\edegree#1{\def\@edegree{#1}}\def\@edegree{}
\def\etitle#1{\def\@etitle{#1}}\def\@etitle{}
\def\eaffil#1{\def\@eaffil{#1}}\def\@eaffil{}
\def\emajor#1{\def\@emajor{#1}}\def\@emajor{}
\def\edirection#1{\def\@edirection{#1}}\def\@edirection{}
\def\eauthor#1{\def\@eauthor{#1}}\def\@eauthor{}
\def\esupervisor#1{\def\@esupervisor{#1}}\def\@esupervisor{}
\def\edate#1{\def\@edate{#1}}\def\@edate{}

\newcommand{\ecnumcc}[1]{\multicolumn{1}{c}{\underline{\makebox[10em][c]{#1}}}}
\newcommand{\ecnumce}[1]{\multicolumn{1}{c}{\underline{\makebox[15em][c]{#1}}}}

\def\makecover{
  \begin{titlepage}
  %%%%% ===== 中文封面
  \phantomsection
  \pdfbookmark[0]{中文封面}{ccover}
  \linespread{1.1}\zihao{4}\ziju{0.05}
  \noindent{\!\@graduateyear\,届博士专业学位研究生学位论文}\smallskip
  \par\noindent\hspace*{-12pt}
  \setlength{\tabcolsep}{2pt}
  \begin{tabular}[t]{rl}
    分\hspace{7.5pt}类\hspace{7.5pt}号：
                      &\ \underline{\makebox[6em][l]{\,\@class}}  \\[1.5ex]
    密\hspace{2.1em}级：&\ \underline{\makebox[6em][l]{\@security}}
  \end{tabular}
  \hfill
  \begin{tabular}[t]{rl}
    学校代码：&\ \underline{\makebox[6em][l]{\,10291}} \\[1.5ex]
    学\hspace{2.2em}号：&\ \underline{\makebox[6em][l]{\,\@studentid}}
  \end{tabular}

  \vspace{4em}
  \begin{center}
%
% 封面学校图标及名称
%  
    \raisebox{-1ex}[0pt][0pt]{\includegraphics[width=0.15\textwidth]{njtech}}\ \ 
	\includegraphics[width=0.75\textwidth,height=6em]{njtech0}

    \bigskip
    {\STSong
      \zihao{-2}\textbf{Nanjing Tech University} \\[0.5ex]
      \zihao{2} 博士学位论文\\[1ex]
      \zihao{-2} \textbf{DOCTORAL~~DISSERTATION}
      %\zihao{2} 博士专业学位论文\\[1ex]
      %\zihao{-2} \textbf{Doctoral's Degree Thesis (Professional)}

    % title
    \vfill\noindent
    \parbox[t]{0.25\textwidth}{\zihao{1} 论文题目：}
    \begin{varwidth}[t]{.75\linewidth}\linespread{1.3}\zihao{1} \@ctitle \end{varwidth}


    \vfill\linespread{1.5}\selectfont\zihao{4}
    \renewcommand{\arraystretch}{1.2}
    \begin{tabular}{p{0cm}p{6.5em}@{\extracolsep{0.5ex}}cc}
     ~ & 院\hfill 系： & & \ecnumcc{\@caffil } \\
     ~ & 专\hfill 业\hfill 学\hfill 位\hfill 类\hfill 别： & & \ecnumcc{\@cmajor}\\
     ~ & 专\hfill 业\hfill 学\hfill 位\hfill 领\hfill 域：& & \ecnumcc{\@cdirection}\\
     ~ & 学\hfill 位\hfill 申\hfill 请\hfill 人：& & \ecnumcc{\@cauthor}\\
     ~ & 指\hfill 导\hfill 教\hfill 师：& & \ecnumcc{\@csupervisor}
    \end{tabular}
    }

    \vfill\@cdate
  \end{center}

  \clearpage{\pagestyle{empty}\cleardoublepage}
  %%%%% ===== 英文封面
  \thispagestyle{empty}
  \phantomsection
  \pdfbookmark[0]{英文封面}{ecover}
  \noindent Dissertation for Doctoral Degree (Professional) in \@graduateyear

  \mbox{}\hfill
  \begin{tabular}[t]{l}
    University Code: 10291 \\[1.5ex]
    Student ID: \makebox[6em][l]{\,\@studentid}
  \end{tabular}


  \vspace{5em}
  \begin{center}
    {\zihao{-0} Nanjing Tech University}
    %\scalebox{1.15}[1.6]{\bfseries NANJING TECH UNIVERSITY}

    % title
    \vspace{6em}{\bfseries
    \parbox[t]{0.125\textwidth}{\zihao{2} Title：}
    \begin{varwidth}[t]{.75\linewidth}\linespread{1.4}\zihao{2} \@etitle \end{varwidth}}

    \vfill\linespread{1.5}\selectfont\mdseries

    \renewcommand{\arraystretch}{1.1}
    \scalebox{1}[1.0]{\setlength{\tabcolsep}{0.5ex}
    \begin{tabular}{rl}
     Department/School: &  \ecnumce{\@eaffil } \\
     Category:   &  \ecnumce{\@emajor}\\
     Field:      &  \ecnumce{\@edirection}\\
     Candidate:  & \ecnumce{\@eauthor}\\
     Supervisor: &  \ecnumce{\@esupervisor}
    \end{tabular}
    }

    \vfill
    \@edate
  \end{center}
\end{titlepage}
}

%%%%% baselineskip
\linespread{1.4}
