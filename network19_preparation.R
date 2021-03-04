# Data preparation for the network 2019


library(data.table)
library(igraph)
library(tidyverse)

# Read in the dataset
comext <- data.table::fread("~/studies/estat-hckt-ee-study/comex/products/full201952.dat",na.strings="",stringsAsFactors = T)

comext <- comext %>% 
  select(-PRODUCT_SITC, -PRODUCT_CPA2002, -PRODUCT_CPA2008, -PRODUCT_CPA2_1, -PRODUCT_BEC, -PRODUCT_SECTION) %>% 
  filter(PRODUCT_NC != "TOTAL")

# Select the codes that are of interest
# cn6 is the combined nomenclature 6 digit variable

puhastus2019 <- comext %>% 
  mutate(cn6 = substr(PRODUCT_NC, 1, 6)) %>% 
  filter(cn6 %in% c("380894", "220710", "220890", "284700", "152000", "392330", "392350"))

# Change the type of the country code to character

puhastus2019$PARTNER_ISO <- as.character(puhastus2019$PARTNER_ISO)
puhastus2019$DECLARANT_ISO <- as.character(puhastus2019$DECLARANT_ISO)

# Removing codes starting with Q, Ceuta XC, Melilla XL
puhastus2019 <- puhastus2019 %>% 
  filter(!PARTNER_ISO %in% c("QP", "QS", "QW", "QZ", "QR", "QV", "XC", "XL"))


# List of unique names of country codes

ctrs <- unique(puhastus2019$PARTNER_ISO)
ctrs <- ctrs[!is.na(ctrs)]

nodes <- data.table::data.table(id=ctrs, code=ctrs, name=countrycode::countrycode(ctrs,origin="iso2c", destination = 'iso.name.en'))
nodes[id=="XK",name:="Kosovo"]
nodes[id=="XS",name:="Serbia"]

write.csv2(nodes, "nodes_puhastus2019.csv")

# Preparing the edges
# Define origin and destination

puhastus_edges <- puhastus2019 %>% 
  mutate(origin = case_when(FLOW == 1 ~ PARTNER_ISO,
                            FLOW == 2 ~ DECLARANT_ISO))

puhastus_edges <- puhastus_edges %>% 
  mutate(destination = case_when(FLOW == 2 ~ PARTNER_ISO,
                                 FLOW == 1 ~ DECLARANT_ISO))

# Change the order (some R visualisation packages want it so)
puhastus_edges <- puhastus_edges %>% 
  select(origin, destination, VALUE_IN_EUROS, everything())

# Calculating the trade flow sums
puhastus2019_edges <- puhastus_edges %>% 
  group_by(origin, destination, cn6, TRADE_TYPE) %>% 
  summarise(weight=sum(VALUE_IN_EUROS)) %>% 
  ungroup()

write.csv2(puhastus2019_edges, "edges_puhastus2019.csv")

