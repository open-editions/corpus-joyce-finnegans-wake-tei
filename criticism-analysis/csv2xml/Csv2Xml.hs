{-# LANGUAGE ScopedTypeVariables #-}
{-# LANGUAGE DeriveGeneric #-}
{-# LANGUAGE OverloadedStrings #-}
{-# LANGUAGE OverloadedLists #-}

import qualified Data.Text.Lazy.IO as Text
import qualified Data.Map as Map
import Text.XML
import qualified Data.ByteString.Lazy as BL
import Data.Csv
import qualified Data.Vector as V
import GHC.Generics (Generic)
import Text.XML

data Matches = Matches { textA :: !String
                       , textB :: !String
                       , threshold :: !Int
                       , cutoff :: !Int
                       , nGrams :: !Int
                       , numMatches :: !Int
                       , textALength :: !Int
                       , textBLength :: !Int
                       , locationsInA :: !String
                       , locationsInB :: !String
                       } deriving (Generic, Show)

instance FromRecord Matches
instance ToRecord Matches

-- Text A,Text B,Threshold,Cutoff,N-Grams,Num Matches,
-- Text A Length,Text B Length,Locations in A,Locations in B

getVecs :: IO (V.Vector Matches)
getVecs = do
    csvData <- BL.readFile "fw-matches-1.csv"
    -- print csvData
    let decoded = decode HasHeader csvData :: Either String (V.Vector Matches)
    let decoded' = case decoded of
                     Left err -> error "Something went wrong"
                     Right v -> v
    return decoded'

-- Let's make this!
-- <?xml version="1.0" encoding="utf-8"?>
-- <standOff type="textMatching">
--   <listBibl>
--     <biblStruct xml:id="id-in-criticism">
--       <!-- bibliographic stuff here -->
--     </biblStruct>
--   </listBibl>
--   <linkGrp>
--     <!-- for each match -->
--     <link target="string-range(#id-in-FW, start, end) string-range(#id-in-criticism, start, end)" />
--     <!-- end for -->
--     </linkGrp>
-- </standOff>

-- helpers
attr_ = (,)
element_ nam attrs bdy = NodeElement $ Element nam (Map.fromList attrs) bdy
text_ = NodeContent

-- elements
listBibl_ = element_ "listBibl"
biblStruct_ = element_ "biblStruct"
linkGrp_ = element_ "linkGrp"
link_ = element_ "link"
standOff_ = element_ "standOff"

-- attributes
target_ = attr_ "target"

-- used to unwrap a top level Node to an Element
unNode (NodeElement x) = x

standOffs = unNode $ standOff_ [] [ bibls, links ]

bibls = listBibl_ [] [ biblStruct_ [] [text_ ""] , biblStruct_ [] [text_ ""] ]

links = linkGrp_ [] [ link_ [ target_ ""  ] [text_ ""] ]

main :: IO ()
main = do
  vecs <- getVecs
  print $ V.head vecs
  Text.putStrLn $ renderText def $ Document (Prologue [] Nothing []) standOffs []
