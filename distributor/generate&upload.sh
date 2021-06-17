find . -type f > mine.txt &
find . -type d > dirs.txt 
sed -i 's \./ \\ g' mine.txt 
sed -i 's / \\ g' mine.txt  
sed -i 's \./ \\ g' dirs.txt 
sed -i 's / \\ g' dirs.txt
git add -A
git commit
git push
