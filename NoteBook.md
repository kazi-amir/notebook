# <p align="center">My CP NoteBook - Kazi Amir Hamza</p>

### 274 Problems Contest by **fahimcp495**

#### Problem: [DK - Rotate and Flip](https://vjudge.net/contest/696883#problem/DK)

#### Constraints: 

$1\leq\ N\ \leq\ 2 \times 10^5$<br>
$1\leq\ M\ \leq\ 2 \ \times 10^5$<br>
$1\leq\ Q\ \leq\ 2 \ \times 10^5$<br>
$-10^9\ \leq\ X_i, Y_i\ \leq\ 10^9$<br>
$-10^9\ \leq\ p_i\ \leq\ 10^9$<br>
$0\ \leq\ A_i\ \leq\ M$<br>
$0\ \leq\ B_i\ \leq\ N$<br>

#### Before any rotation, 0&deg; rotation:
$$
\[
\begin{pmatrix}
  1       & 0   & 0  \\
  0       & 1   & 0  \\
  0       & 0   & 1  \\
\end{pmatrix}
\begin{pmatrix}
  x  \\
  y  \\
  1  \\
\end{pmatrix}
=
\begin{pmatrix}
  x  \\
  y  \\
  1  \\
\end{pmatrix}
\]
$$

#### After operation 1, 90&deg; clockwise rotation:
$$
\[
\begin{pmatrix}
  0       & 1   & 0  \\
  -1      & 1   & 0  \\
  0       & 0   & 1  \\
\end{pmatrix}
\begin{pmatrix}
  x  \\
  y  \\
  1  \\
\end{pmatrix}
=
\begin{pmatrix}
  y  \\
  -x  \\
  1  \\
\end{pmatrix}
\]
$$

#### After operation 2, 90&deg; counter clockwise rotation:
$$
\[
\begin{pmatrix}
  0       & -1  & 0  \\
  1       & 0   & 0  \\
  0       & 0   & 1  \\
\end{pmatrix}
\begin{pmatrix}
  x  \\
  y  \\
  1  \\
\end{pmatrix}
=
\begin{pmatrix}
  -y  \\
  x  \\
  1  \\
\end{pmatrix}
\]
$$

#### After operation 3, Mirror reflection at point **p** on **x** axis:
$$
\[
\begin{pmatrix}
  -1      & 0   & 2p  \\
  0       & 1   & 0  \\
  0       & 0   & 1  \\
\end{pmatrix}
\begin{pmatrix}
  x  \\
  y  \\
  1  \\
\end{pmatrix}
=
\begin{pmatrix}
  2p-x  \\
  y  \\
  1  \\
\end{pmatrix}
\]
$$

#### After operation 4, Mirror reflection at point __p__ on **y** axis:
$$
\[
\begin{pmatrix}
  1       & 0   & 0  \\
  0       & -1  & 2p  \\
  0       & 0   & 1  \\
\end{pmatrix}
\begin{pmatrix}
  x  \\
  y  \\
  1  \\
\end{pmatrix}
=
\begin{pmatrix}
  x  \\
  2p-y  \\
  1  \\
\end{pmatrix}
\]
$$
