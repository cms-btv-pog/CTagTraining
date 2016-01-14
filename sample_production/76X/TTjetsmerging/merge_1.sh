CAT=(CombinedSVRecoVertexNoSoftLepton CombinedSVPseudoVertexNoSoftLepton CombinedSVNoVertexNoSoftLepton CombinedSVRecoVertexSoftElectron CombinedSVPseudoVertexSoftElectron CombinedSVNoVertexSoftElectron CombinedSVRecoVertexSoftMuon CombinedSVPseudoVertexSoftMuon CombinedSVNoVertexSoftMuon)
#CAT=(CombinedSVRecoVertexNoSoftLepton CombinedSVPseudoVertexNoSoftLepton CombinedSVNoVertexNoSoftLepton CombinedSVRecoVertexSoftElectron CombinedSVNoVertexSoftElectron CombinedSVRecoVertexSoftMuon CombinedSVNoVertexSoftMuon )

FLAV=(D U S G)

for k in ${CAT[@]} ;
do
#		echo ${k}_D.root
		hadd tmp.root ${k}_D.root ${k}_U.root ${k}_S.root ${k}_G.root
		mv tmp.root ${k}_DUSG.root
#	for i in ${FLAV[@]} ;
#	do
#		echo cat ${k}${i}files.txt
#		rootfiles=`cat ${k}${i}files.txt`
#		hadd tmp.root $rootfiles
#		mv tmp.root ${k}_${i}.root
#	done
done

