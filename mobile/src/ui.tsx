import React from 'react';
import { Pressable, Text, StyleSheet, TextInput, View, TextInputProps } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
export const C={bg:'#F7F8F3',paper:'#FFFFFF',ink:'#182E28',muted:'#697770',green:'#235C48',lime:'#DCE9BE',line:'#E3E8DE',red:'#B5483E'};
export function Button({title,onPress,secondary=false,disabled=false,icon}:{title:string;onPress:()=>void;secondary?:boolean;disabled?:boolean;icon?:React.ComponentProps<typeof Ionicons>['name']}){
 return <Pressable accessibilityRole="button" disabled={disabled} onPress={onPress} style={({pressed})=>[u.button,{backgroundColor:secondary?C.bg:C.green,opacity:disabled?.45:pressed?.7:1},secondary&&{borderWidth:1,borderColor:C.line}]}>{icon&&<Ionicons name={icon} size={19} color={secondary?C.green:'white'}/>}<Text style={{fontWeight:'700',color:secondary?C.green:'white',fontSize:14}}>{title}</Text></Pressable>;
}
export function Field({label,...props}:TextInputProps&{label:string}){return <View style={{gap:6}}><Text style={u.label}>{label}</Text><TextInput accessibilityLabel={label} placeholderTextColor={C.muted} {...props} style={[u.input,props.multiline&&{minHeight:120,textAlignVertical:'top'},props.style]}/></View>}
export const u=StyleSheet.create({button:{minHeight:48,borderRadius:14,justifyContent:'center',alignItems:'center',padding:12,flexDirection:'row',gap:8},input:{backgroundColor:C.paper,borderWidth:1,borderColor:C.line,borderRadius:12,padding:13,fontSize:15,color:C.ink},label:{fontSize:13,fontWeight:'600',color:C.muted},card:{backgroundColor:C.paper,padding:18,borderRadius:22,borderWidth:1,borderColor:C.line,gap:12},h2:{fontSize:22,fontWeight:'700',color:C.ink},text:{fontSize:15,lineHeight:24,color:C.ink},muted:{fontSize:13,lineHeight:20,color:C.muted}});
