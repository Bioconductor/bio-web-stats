# global_package_history.R
library(glue)
# create a data frame consisting of release, biocViews category, package for all history
# Assumes the git.bioconductor.org:admin/manifest project has been cloned to this directory

repo_location <- "~/Projects/manifest/"
outfile_location <- "~/Downloads/manifest_to_packages_table.csv"
table_data_location <- "~/Downloads/packages_table-data.csv"

setwd(repo_location)
system2(c("git","fetch","--all"), stdout = TRUE)
branch_list <- trimws(system2(c("git","branch","-r"), stdout = TRUE))
branch_list <- branch_list[startsWith(branch_list, "origin/RELEASE_")]
names(branch_list) <- sapply(strsplit(branch_list, "_"), (\(u) as.numeric(u[2])*100+as.numeric(u[3])))
branch_list <- branch_list[order(names(branch_list))]

result <- Reduce(rbind, mapply((\(u, version_id) {
    system(glue("git checkout {u}"))
    files = dir(pattern = "*.txt")
    names(files) <- sapply(strsplit(files, ".", fixed = TRUE), (\(u) u[1]))
    Reduce(rbind,mapply((\(v, category) {
       x <- readLines(v)
       packages <- sapply(x[startsWith(x, "Package:")], (\(z) {
          trimws(strsplit(z, "Package:")[[1]][2])
         }), USE.NAMES = FALSE)
       data.frame(version=version_id, category=category, package=packages)
    }), files, sapply(strsplit(files, ".", fixed = TRUE), (\(u) u[1])), SIMPLIFY = FALSE))
  }), 
    branch_list,
    sapply(strsplit(branch_list, "_"), 
           (\(u) paste0("v", as.character(as.numeric(u[2])*100+as.numeric(u[3])), collapse = ""))),
    SIMPLIFY = FALSE
))

# write.csv(result, "manifest_matrix.csv")
result <- read.csv("/Users/rshear/Downloads/manifest_matrix.csv")

p_c <- unique(result[,c("package", "category")])
x <-split(p_c$category, p_c$package)

# Packages in 2 or more categories
multi_cat <- x[which(sapply(split(p_c$category, p_c$package), length) > 1)]
length(multi_cat)
# packages in software testing
swt_pac <- p_c[p_c$category == "software-testing", "package"]
table(p_c[p_c$package %in% swt_pac,])

# ignore the (software, software-testing) pairs
i <- sapply(multi_cat, (\(u) !identical(sort(u),c( "software","software-testing"))))
multi_cat2 <- multi_cat[i]

r3 <- result[result$package %in% names(multi_cat2),]
r3s <- split(r3, r3$package)
for (i in r3s) {
  print(glue("\n{i$package[1]}\n"))
  x <- split(i, i$category)
  for (j in x) {
    r <- range(j$version)
    print(glue("\t{j$category[1]}\t{r[1]}-{r[2]}"))
  }
}


# Here is the generation of the database table
table_data <- Reduce(rbind, lapply(split(result, result$package), (\(i) {
  u <- i[order(i$version),]
  first <- u$version[1]
  last <- u$version[nrow(u)]
  if (last == "v318") {
    last <- ""
  }
  data.frame(category=u$category[1], package=u$package[1], first, last)
  }
)))
write.csv(table_data, table_data_location, col.names = FALSE)
