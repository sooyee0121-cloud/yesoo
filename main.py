import streamlit as st
st.title('나의 첫 웹서비스 만들기!')
a=st.text_input('안녕하세요! 만나서 반가워요!')
b=st.selectbox('좋아하는 음식을 선택하세요!',['오페라케이크','된장찌개','까르보나라'])
if st.button('인사말 생성'):
  st.write(a+'님 안녕하세요! 반갑습니다!')
  st.write(b+'를 좋아하시는군요! 저도 좋아해요!')
  st.error('반가워요!!')
  st.balloons()
