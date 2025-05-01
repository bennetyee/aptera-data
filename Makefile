all:	aptera_data coupon_round

aptera_data: any
	ln -f $^ $@

coupon_round: any
	ln -f $^ $@

# cat is needed because otherwise zip seeks to beginning of file and
# overwrites the #! string
any:	*.py
	rm -f any; (echo '#!/usr/bin/python3'; zip - $^) | cat > $@ && chmod +x $@

clean:
	rm -f coupon_round any.zip any *~

.PHONY:	clean all
